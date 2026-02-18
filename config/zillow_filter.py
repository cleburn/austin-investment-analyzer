"""
Shared Zillow data filtering utility.

Provides filtering for raw Zillow ZHVI DataFrames using metros.yaml
as the single source of truth. Used by both the ML training notebook
and process_data.py.

Two filtering modes:
- Metro-column matching (broad): for ML training, captures ALL neighborhoods
  in a metro area by matching the Zillow Metro column against zillow_metro
  values from metros.yaml. Includes state verification as a safety net.
- City+state matching (narrow): for the app's process_data.py, captures only
  neighborhoods in explicitly listed cities.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional

from .metro_config import MetroConfigLoader, get_config_loader


# Training metro groupings: display_metro → training_metro
# DFW and South Florida train as combined groups; all others map to themselves.
TRAINING_METRO_MAP = {
    'dallas': 'dfw',
    'fort_worth': 'dfw',
    'miami': 'south_florida',
    'fort_lauderdale': 'south_florida',
}


def get_training_metro(display_metro: str) -> str:
    """Map a display_metro to its training_metro group."""
    return TRAINING_METRO_MAP.get(display_metro, display_metro)


def build_city_state_lookup(loader: Optional[MetroConfigLoader] = None) -> Dict[Tuple[str, str], str]:
    """
    Build {(city, state): display_metro} from metros.yaml.

    Each metro's zillow_cities (or single zillow_city) is mapped to that
    metro's key as the display_metro. City names are stored as-is (matching
    Zillow's casing), state as the 2-letter code.

    Returns:
        Dict mapping (city, state) tuples to display_metro keys.
    """
    if loader is None:
        loader = get_config_loader()

    lookup = {}
    for metro_key in loader.list_metros():
        config = loader.get_metro(metro_key)
        for city in config.get_zillow_cities():
            lookup[(city, config.state)] = metro_key
    return lookup


def _build_metro_column_lookup(loader: MetroConfigLoader) -> Dict[str, List[str]]:
    """
    Build {zillow_metro_value: [display_metro_key, ...]} from metros.yaml.

    Multiple display metros can share a zillow_metro value (e.g., dallas and
    fort_worth both use "Dallas-Fort Worth-Arlington, TX").
    """
    metro_lookup: Dict[str, List[str]] = {}
    for metro_key in loader.list_metros():
        config = loader.get_metro(metro_key)
        zillow_metro = config.zillow_metro
        if zillow_metro not in metro_lookup:
            metro_lookup[zillow_metro] = []
        metro_lookup[zillow_metro].append(metro_key)
    return metro_lookup


def _assign_display_metro(row: pd.Series,
                          city_lookup: Dict[Tuple[str, str], str],
                          zillow_metro_keys: List[str]) -> str:
    """
    Assign display_metro for a row within a shared zillow_metro area.

    For metros with a single display_metro (e.g., Austin), returns that key.
    For combined metros (DFW, South Florida), uses the city+state lookup
    to split into display metros (dallas vs fort_worth, miami vs fort_lauderdale).
    Cities not in metros.yaml default to the first display_metro in the group
    (e.g., 'dallas' for DFW, 'miami' for South Florida).
    """
    if len(zillow_metro_keys) == 1:
        return zillow_metro_keys[0]

    # Multiple display metros share this zillow_metro — disambiguate by city
    city_state = (row['City'], row['State'])
    return city_lookup.get(city_state, zillow_metro_keys[0])


def filter_zillow_to_metros(df: pd.DataFrame,
                            loader: Optional[MetroConfigLoader] = None) -> pd.DataFrame:
    """
    Filter a raw Zillow DataFrame to target metros using Metro column matching.

    Matches the Zillow Metro column against zillow_metro values from metros.yaml.
    This captures ALL neighborhoods in a metro area (broad coverage for ML training).
    State is verified via metros.yaml config as a safety net.

    For combined metros (DFW, South Florida), uses city+state lookup to assign
    the correct display_metro. Cities not in metros.yaml default to the first
    display_metro in the group (e.g., 'dallas' for DFW, 'miami' for South Florida).

    Adds columns:
        - display_metro: the user-facing metro key (e.g., 'dallas', 'fort_worth')
        - training_metro: the training group (e.g., 'dfw', 'south_florida')

    Args:
        df: Raw Zillow ZHVI DataFrame with Metro, City, State, RegionType columns.
        loader: Optional MetroConfigLoader instance. Uses singleton if None.

    Returns:
        Filtered DataFrame with display_metro and training_metro columns added.
    """
    if loader is None:
        loader = get_config_loader()

    metro_col_lookup = _build_metro_column_lookup(loader)
    city_lookup = build_city_state_lookup(loader)

    # Filter to neighborhoods only
    df_filtered = df[df['RegionType'] == 'neighborhood'].copy()

    # Match Metro column against zillow_metro values
    df_filtered = df_filtered[df_filtered['Metro'].isin(metro_col_lookup.keys())].copy()

    # Assign display_metro
    df_filtered['display_metro'] = df_filtered.apply(
        lambda row: _assign_display_metro(
            row, city_lookup, metro_col_lookup.get(row['Metro'], [])
        ),
        axis=1
    )

    # Add training metro
    df_filtered['training_metro'] = df_filtered['display_metro'].apply(get_training_metro)

    return df_filtered


def filter_zillow_for_metro(df: pd.DataFrame,
                            metro_key: str,
                            loader: Optional[MetroConfigLoader] = None) -> pd.DataFrame:
    """
    Filter a raw Zillow DataFrame for a single metro using city+state matching.

    This is the narrow filter used by process_data.py. Only includes neighborhoods
    in cities explicitly listed in metros.yaml for the given metro.

    Args:
        df: Raw Zillow ZHVI DataFrame with City, State, RegionType columns.
        metro_key: The metro identifier (e.g., 'austin', 'houston').
        loader: Optional MetroConfigLoader instance. Uses singleton if None.

    Returns:
        Filtered DataFrame for the specified metro.
    """
    if loader is None:
        loader = get_config_loader()

    config = loader.get_metro(metro_key)
    cities = config.get_zillow_cities()

    return df[
        (df['RegionType'] == 'neighborhood') &
        (df['City'].isin(cities)) &
        (df['State'] == config.state)
    ].copy()
