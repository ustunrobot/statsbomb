"""
Plugin Registry
---------------
Central registry of all available KPI plugins.

To add a new plugin:
    1. Create kpi/plugins/your_plugin.py implementing BaseKPIPlugin
    2. Import it here
    3. Add an instance to PLUGIN_REGISTRY

No other layer needs to change. The ContextEngine and pipeline
discover plugins automatically through this registry.

Tagging convention (set on each plugin class):
    Scope:    'team' | 'player'
    Domain:   'attacking' | 'defensive' | 'set_piece' | 'tactical' | 'physical'
    Priority: 'core' | 'supplementary' | 'experimental'
    Audience: 'recruitment' | 'coaching_staff' | 'board'
"""

from kpi.plugins.xg_team import XGTeamPlugin
from kpi.plugins.xg_player import XGPlayerPlugin

# ---------------------------------------------------------------------------
# Registry — dict keyed by plugin_id
# ---------------------------------------------------------------------------

PLUGIN_REGISTRY: dict = {
    plugin.plugin_id: plugin
    for plugin in [
        XGTeamPlugin(),
        XGPlayerPlugin(),

        # ---------------------
        # TODO: add plugins as they are built
        # ---------------------
        # PPDAPlugin(),             # Passes Allowed Per Defensive Action
        # SetPieceTeamPlugin(),     # Set piece xG attack/defence
        # FinishingQualityPlugin(), # Post-shot xG team level
        # ProgressivePlayPlugin(),  # Progressive carries and passes
        # PressurePlugin(),         # Press intensity and success rate
        # GoalkeeperPlugin(),       # GK xG prevented / post-shot xGA
        # RecruitmentProfilePlugin(), # Combined player profile for recruitment
    ]
}


def get_plugin(plugin_id: str):
    """Retrieve a plugin by ID. Returns None if not found."""
    return PLUGIN_REGISTRY.get(plugin_id)


def list_plugins(tag: str = None) -> list:
    """
    List all registered plugins, optionally filtered by tag.

    Args:
        tag: Optional tag to filter by (e.g. 'team', 'core', 'recruitment')

    Returns:
        List of plugin instances
    """
    plugins = list(PLUGIN_REGISTRY.values())
    if tag:
        plugins = [p for p in plugins if tag in p.tags]
    return plugins
