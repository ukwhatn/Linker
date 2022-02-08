from __future__ import annotations

from copy import deepcopy

import discord
from discord.ext import commands, tasks
from discord.commands import slash_command, Option
import random
import string
import mysql.connector
from config import server as server_config, bot as bot_config, database as database_config


class RoleChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.linkerAccounts = {}  # {<DiscordID>: {DB Entry}}
        self.regisiteredRoles = {}  # {<GuildID>: {<RoleID>: {DB Entry}}}

        self.updateRegisiteredRoles()
        self.updateLinkerAccounts()

    @commands.Cog.listener()
    async def on_ready(self):
        """on_ready時に発火する関数
        """
        pass
        # self.updateTask.stop()
        # self.updateTask.start()

    @staticmethod
    def randomname(n):
        if bot_config.DEVMODE:
            randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
            return "_" + "".join(randlst).lower()
        else:
            return ""

    def updateLinkerAccounts(self):
        con = mysql.connector.connect(**database_config.account)
        with con.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM Accounts WHERE WikidotVerified = 1")
            accounts = cursor.fetchall()
            if accounts is None:
                self.linkerAccounts = {}
            else:
                self.linkerAccounts = {a["DiscordID"]: a for a in accounts}
        return

    def updateRegisiteredRoles(self):
        con = mysql.connector.connect(**database_config.account)
        with con.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM DiscordRoles WHERE isEnable = 1")
            regisiteredRoles = cursor.fetchall()
            if regisiteredRoles is None:
                self.regisiteredRoles = {}
            else:
                for a in regisiteredRoles:
                    if a["GuildID"] not in self.regisiteredRoles:
                        self.regisiteredRoles[a["GuildID"]] = {}
                    self.regisiteredRoles[a["GuildID"]][a["RoleID"]] = a
        return

    @slash_command(name="p" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def ping(self, ctx):
        await ctx.respond("pong!")

    @slash_command(name="addrole" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def addRole(self, ctx,
                      role: Option(str, "対象ロールをメンション"),
                      is_linked: Option(int, "Linker登録有無(1/0)", choices=[-1, 0, 1], required=True),
                      is_jp: Option(int, "JPメンバ登録有無(1/0)", choices=[-1, 0, 1], required=True)):
        if is_linked == 0 and is_jp in (0, 1):
            # Linker未登録ではJPメンバかどうか判定不可能
            await ctx.respond("JPメンバ登録があるかどうかを判定条件に加える場合は、Linker登録有無を1にしてください。")
            return

        else:
            roleId = int(role.removeprefix("<@").removeprefix("&").removesuffix(">"))

            con = mysql.connector.connect(**database_config.account)
            with con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO DiscordRoles (GuildID, RoleID, IsLinked, IsJPMember) VALUES(%s, %s, %s, %s)"
                    "ON DUPLICATE KEY UPDATE IsLinked = %s, IsJPMember = %s",
                    (ctx.guild.id, roleId, is_linked, is_jp, is_linked, is_jp))
            con.commit()
            await ctx.respond("\n".join([
                f"{role} を以下の条件で追加/更新しました。",
                f"> Guild: {ctx.guild.name}({ctx.guild.id})",
                f"> Linker: {'登録済' if is_linked == 1 else '指定なし' if is_linked == -1 else '未登録'}",
                f"> JPメンバ登録: {'登録済' if is_jp == 1 else '指定なし' if is_jp == -1 else '未登録'}"
            ]))
            self.updateRegisiteredRoles()

    async def searchUserAndAddRole(self, targetGuild: discord.Guild | None = None):
        # データ更新
        self.updateRegisiteredRoles()
        self.updateLinkerAccounts()

        regisiteredRoles = deepcopy(self.regisiteredRoles)
        linkerAccounts = deepcopy(self.linkerAccounts)

        for guildId in regisiteredRoles:

            # Guild指定がある場合はここでそれ以外を止める
            if targetGuild is not None and targetGuild.id != guildId:
                continue

            # Guildインスタンスを取得
            guild = self.bot.get_guild(guildId)

            if guild is None:
                # Guildが見つからなければ次へ
                continue

            # Guildに指定されているロールを存在確認しながら列挙
            # iterateしつつ、Remove時にも使う
            regisiteredRolesOnGuild = []
            for roleId in regisiteredRoles[guildId]:
                # Roleインスタンス取得
                role = guild.get_role(roleId)
                if role is not None:
                    regisiteredRolesOnGuild.append(role)

            # Remove除外用処理済RoleIDリスト
            processedRoleIDsOnGuild = []

            for role in regisiteredRolesOnGuild:

                # 処理済に追加
                processedRoleIDsOnGuild.append(role.id)

                isLinked = regisiteredRoles[guildId][role.id]["IsLinked"]
                isJPMember = regisiteredRoles[guildId][role.id]["IsJPMember"]

                if isLinked == 1:
                    isLinked = True
                elif isLinked == 0:
                    isLinked = False
                else:
                    isLinked = None

                if isJPMember == 1:
                    isJPMember = True
                elif isJPMember == 0:
                    isJPMember = False
                else:
                    isJPMember = None

                # エラー除外
                if isLinked is False and (isJPMember is True or isJPMember is False):
                    continue

                elif isJPMember is True:
                    # Linker登録済かつJPメンバ
                    # TODO: 実装
                    pass
                elif isJPMember is False:
                    # Linker登録済かつJPメンバではない
                    # TODO: 実装
                    pass
                else:
                    # JPメンバかどうかは問わない
                    regisiteredAccountIDs = linkerAccounts.keys()
                    for _discordUser in guild.members:

                        # botアカウント除外
                        if _discordUser.bot:
                            continue

                        # 既存未処理Role剥奪
                        _removeTarget = []
                        for _role in regisiteredRolesOnGuild:
                            if _role.id not in processedRoleIDsOnGuild:
                                _removeTarget.append(role)
                        await _discordUser.remove_roles(*_removeTarget)

                        if isLinked is True:
                            # Linker登録済
                            if _discordUser.id in regisiteredAccountIDs:
                                # 登録済ならRole付与
                                await _discordUser.add_roles(role)

                        elif isLinked is False:
                            # Linker未登録
                            if _discordUser.id not in regisiteredAccountIDs:
                                # 未登録ならRole付与
                                await _discordUser.add_roles(role)

                    else:
                        # ギルド内全員
                        # TODO: 実装
                        pass

    @slash_command(name="force_update" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def forceUpdate(self, ctx):
        if bot_config.DEVMODE:
            print("メソッド開始")

        await ctx.respond("強制アップデートを開始します")

        if bot_config.DEVMODE:
            print("処理開始")

        await self.searchUserAndAddRole(targetGuild=ctx.guild)

        if bot_config.DEVMODE:
            print("処理終了")

        await ctx.respond("強制アップデートを完了しました")

        if bot_config.DEVMODE:
            print("メソッド終了")

    @tasks.loop(minutes=30)
    async def updateTask(self):
        if bot_config.DEVMODE:
            print("Update Start")
        await self.searchUserAndAddRole()
        if bot_config.DEVMODE:
            print("Update Finished")

    @slash_command(name="reload_update_task" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def reloadUpdateTask(self, ctx):
        self.updateTask.stop()
        self.updateTask.start()
        await ctx.respond("Done")


def setup(bot):
    return bot.add_cog(RoleChecker(bot))
