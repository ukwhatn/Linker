from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Code by being24
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if hasattr(ctx.command, 'on_error'):  # ローカルのハンドリングがあるコマンドは除く
            return

        elif isinstance(error, commands.errors.MissingPermissions):
            await ctx.respond(f"You have no permission to execute {ctx.command.name}.")
            return

        else:
            error = getattr(error, 'original', error)
            error_content = f'error content: {error}\nmessage_content: {ctx.command.name}\nmessage_author : {ctx.author}\nguild: {ctx.interaction.guild}\nchannnel: {ctx.interaction.channel}'
            await ctx.respond(error_content)
            return


def setup(bot):
    return bot.add_cog(ErrorHandler(bot))
