"""Shows plugins that are loaded"""
import colors
import common
import logger
import plugin_api


_logger = logger.LOGGER


class Plugin(plugin_api.LocalPlugin):
    """Plugin to show loaded plugins"""

    @property
    def enabled(self):
        """ALWAYS ENABLED!"""
        return True

    async def on_message(self, target, by, message):
        if message == '.plugins list':
            plugin_list = []
            for name, plugin in self.client.plugins.items():
                if plugin.enabled:
                    plugin_list.append(
                        colors.colorize(name, fg=colors.GREEN)
                    )
                else:
                    plugin_list.append(
                        colors.colorize(name, fg=colors.RED)
                    )
            await self.client.message(
                target,
                ', '.join(sorted(plugin_list))
            )
        if message == '.plugins reload':
            if not await common.is_user_admin(self.client, by):
                _logger.info('%s is not an admin, cant reload plugins')
                return
            self.client.plugins = common.load_py_plugins(
                self.client.chatnet,
                reload=True
            )
            await self.client.message(
                target,
                f'🔌 {colors.BOLD}R E L O A D E D{colors.BOLD} 🔌'
            )

    def help_msg(self):
        return {
            'list': 'use ".plugins list" to list loaded plugins',
            'reload': 'use ".plugins reload" to reload all plugins'
        }
