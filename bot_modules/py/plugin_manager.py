"""Shows plugins that are loaded"""
import colors
import common
import plugin_api


class Plugin(plugin_api.LocalPlugin):
    """Plugin to show loaded plugins"""

    async def on_message(self, target, by, message):
        if message == '.plugins':
            await self.client.message(
                target,
                ','.join(list(self.client.plugins.keys()))
            )
        if message == '.plugins reload':
            self.client.plugins = common.reload_py_plugins()
            for _, plugin in self.client.plugins.items():
                plugin.on_loaded(self.client)
            await self.client.message(
                target,
                f'🔌 {colors.BOLD}R E L O A D E D{colors.BOLD} 🔌'
            )

    def help_msg(self):
        return {
            'show': 'use ".plugins" to show loaded plugins',
            'reload': 'use ".plugins reload" to reload all plugins'
        }

