# TODO: Initialize the Dify Plugin SDK and register provider + tools
# Entry point for the Dynatrace Dify Plugin

from dify_plugin import DifyPluginEnv, Plugin

plugin = Plugin(DifyPluginEnv())

if __name__ == '__main__':
    plugin.run()
