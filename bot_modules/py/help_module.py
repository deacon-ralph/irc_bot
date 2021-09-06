"""Help module, which displays help info for plugins"""
import colors
import plugin_api


class Plugin(plugin_api.LocalPlugin):
    """Help plugin"""

    @property
    def enabled(self):
        """ALWAYS ENABLED!"""
        return True

    def help_msg(self):
        return {
            'usage': '.help <module> <detail>',
            'example_detail': 'this is an example help detail'
        }

    async def on_message(self, target, by, message):
        if message.startswith('.help '):
            parts = message.split(' ')
            if len(parts) == 2:
                plugin = self.client.plugins.get(parts[1])
                if plugin:
                    await self.client.message(
                        target,
                        colors.colorize(plugin.showhelp(), fg=colors.LIGHT_BLUE)
                    )
                else:
                    await self.client.message(
                        target,
                        colors.colorize(
                            f'plugin {parts[1]} not found',
                            colors.WHITE,
                            colors.RED
                        )
                    )
            if len(parts) == 3:
                plugin = self.client.plugins.get(parts[1])
                if plugin:
                    await self.client.message(
                        target,
                        colors.colorize(
                            plugin.showhelp(parts[2]),
                            fg=colors.LIGHT_BLUE)
                    )
                else:
                    await self.client.message(
                        target,
                        colors.colorize(
                            f'plugin {parts[1]} not found',
                            colors.WHITE,
                            colors.RED
                        )
                    )
