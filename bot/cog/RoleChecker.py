import logging
import random
import string

import discord
import mysql.connector
from discord.commands import slash_command, Option
from discord.ext import commands, tasks

from config import server as server_config, bot as bot_config, database as database_config


class RoleChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.linkerAccounts = {}  # {<DiscordID>: {DB Entry}}
        self.regisiteredRoles = {}  # {<GuildID>: {<RoleID>: {DB Entry}}}
        self.jpMembers = []

        self.updateRegisiteredRoles()
        self.updateLinkerAccounts()
        self.updateNoahInformations()

        self.logger = logging.getLogger("LinkerBot")

    @staticmethod
    def randomname(n):
        if bot_config.FORCE_COMMAND_UPDATE:
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

    def updateNoahInformations(self):
        con = mysql.connector.connect(**database_config.account)
        with con.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT a.DiscordID FROM Accounts a INNER JOIN Noah.SiteMembers sm ON sm.userID = a.WikidotID AND sm.siteID = 578002")
            jpMembers = cursor.fetchall()
        jpMembers = [u["DiscordID"] for u in jpMembers]
        self.jpMembers = jpMembers
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

    def isLinkerVerified(self, user: discord.Member):
        return user.id in self.linkerAccounts.keys()

    def isJPMember(self, user: discord.Member):
        return user.id in self.jpMembers

    def updateDiscordAccountsTable(self, targetGuild: discord.Guild = None):
        self.updateRegisiteredRoles()
        self.updateLinkerAccounts()
        self.updateNoahInformations()
        bot: discord.Client = self.bot
        stmt_insert = []
        for guild in bot.guilds:
            if targetGuild is not None and guild.id != targetGuild.id:
                continue
            for member in guild.members:
                if not member.bot:
                    stmt_insert.append((guild.id, member.id, member.joined_at, self.isLinkerVerified(member), self.isJPMember(member)))
        con = mysql.connector.connect(**database_config.account)
        with con.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO DiscordAccounts (GuildID, UserID, JoinDate, isLinkerVerified, isJPMember) VALUES (%s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE isLinkerVerified = VALUES(isLinkerVerified), isJPMember = VALUES(isJPMember)",
                stmt_insert
            )
        con.commit()

    def getLatestUpdatedRowFromDiscordAccountsTable(self):
        con = mysql.connector.connect(**database_config.account)
        with con.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM DiscordAccounts WHERE latestUpdated = (SELECT DISTINCT latestUpdated FROM DiscordAccounts ORDER BY latestUpdated DESC LIMIT 1) "
                           "AND latestUpdated >= (NOW() - INTERVAL 30 SECOND)")
            rows = cursor.fetchall()
        return rows

    async def addRolesToUpdatedMembersOnGuild(self, targetGuild: discord.Guild = None):
        # テーブルを更新
        self.logger.info("テーブル更新")
        self.updateDiscordAccountsTable(targetGuild)

        # 更新されたユーザを取得
        self.logger.info("ターゲットユーザ取得")
        users = self.getLatestUpdatedRowFromDiscordAccountsTable()
        # 整形
        usersPerGuild = {}
        for user in users:
            if user["GuildID"] not in usersPerGuild:
                usersPerGuild[user["GuildID"]] = []
            usersPerGuild[user["GuildID"]].append(user)

        # 登録ロールをGuildごとに見る
        for guildID in self.regisiteredRoles:
            # Guildを取得
            guild: discord.Guild = self.bot.get_guild(guildID)

            # Guildがなければとばす
            if guild is None:
                continue

            # Guildの指定があったらそれ以外を飛ばす
            if targetGuild is not None and guild.id != targetGuild.id:
                continue

            self.logger.info(f"処理開始: {guild.name}")

            # 更新されたユーザのうち、このGuildに参加しているユーザを取得
            if guildID in usersPerGuild:
                usersInGuild = usersPerGuild[guildID]
            else:
                continue

            # Guild内のターゲットロールを列挙(削除用)
            roleObjsInGuild = []
            for roleID in self.regisiteredRoles[guildID].keys():
                roleObj: discord.Role = guild.get_role(roleID)
                if roleObj is not None:
                    roleObjsInGuild.append(roleObj)

            # 対象ユーザからターゲットロールをすべて剥奪
            for user in usersInGuild:
                userObj = guild.get_member(user["UserID"])
                if userObj is not None and not userObj.bot:
                    userRoleIDs = [role.id for role in userObj.roles]
                    for role in roleObjsInGuild:
                        if role.id in userRoleIDs:
                            await userObj.remove_roles(*roleObjsInGuild)
                            self.logger.info(f"ロール削除: {userObj.name}")
                            break

            rolesToAdd = {}

            # ロールごとに見る
            for roleID, roleDatas in self.regisiteredRoles[guildID].items():
                # ロールオブジェクト取得
                role = guild.get_role(roleID)

                # ロールがなければとばす
                if role is None:
                    continue

                # 対象ユーザごとに見る
                for user in usersInGuild:
                    # ロールの条件と合致したらロールをつける
                    if (roleDatas["IsLinked"] == -1 or (roleDatas["IsLinked"] == user["isLinkerVerified"])) and (
                            roleDatas["IsJPMember"] == -1 or (roleDatas["IsJPMember"] == user["isJPMember"])):
                        userObj = guild.get_member(user["UserID"])
                        if userObj is not None and not userObj.bot:
                            if userObj.id not in rolesToAdd:
                                rolesToAdd[userObj.id] = []
                            rolesToAdd[userObj.id].append(role)

            for userID, roles in rolesToAdd.items():
                userObj = guild.get_member(userID)
                if userObj is not None and not userObj.bot:
                    await userObj.add_roles(*roles)
                    self.logger.info(f"ロール付与: {userObj.name}, {','.join([role.name for role in roles])}")

    @slash_command(name="force_update" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def forceUpdate(self, ctx):
        self.logger.infot("メソッド開始")

        await ctx.respond("強制アップデートを開始します")

        await self.addRolesToUpdatedMembersOnGuild(targetGuild=ctx.guild)

        await ctx.respond("強制アップデートを完了しました")

        self.logger.info("メソッド終了")

    @tasks.loop(minutes=1)
    async def updateTask(self):
        logging.info("Update Start")
        await self.addRolesToUpdatedMembersOnGuild()
        logging.info("Update Finished")

    @slash_command(name="reload_update_task" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def reloadUpdateTask(self, ctx):
        self.updateTask.stop()
        self.updateTask.start()
        await ctx.respond("Done")

    @slash_command(name="stop_update_task" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def stopUpdateTask(self, ctx):
        self.updateTask.stop()
        await ctx.respond("Done")

    @slash_command(name="start_update_task" + randomname(3), guild_ids=server_config.CORE_SERVERS)
    @commands.has_permissions(ban_members=True)
    async def startUpdateTask(self, ctx):
        self.updateTask.start()
        await ctx.respond("Done")


def setup(bot):
    return bot.add_cog(RoleChecker(bot))
