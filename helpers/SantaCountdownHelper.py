import pendulum
from discord.ext import commands

import helpers.BOT_ERROR as BOT_ERROR
from helpers.SQLiteHelper import SQLiteHelper
import CONFIG

class SantaCountdownHelper():
    def __init__(self, sqlitehelper: SQLiteHelper):
        self.pend_format = "M/D/YY [@] h:m A Z"
        self.cd_table_name = "Countdowns"
        self.sqlhelp = sqlitehelper

    def __get_cd_table_name(self, guild_id: str):
        return f"{self.cd_table_name}_{guild_id}"

    def __countdown_cmd_set(self, ctx: commands.Context, cd_name: str, cd_time: str):
        result_str = ""
        try:
            pend_test_convert = pendulum.from_format(cd_time, self.pend_format) # check that the format is correct
            if(self.sqlhelp.insert_records(self.__get_cd_table_name(ctx.guild.id), "(name, time, user_id)", [f"('{cd_name}', '{cd_time}', {ctx.author.id})"])):
                diff_str = self.__find_pend_diff_str(pend_test_convert)
                result_str = f"{cd_name} countdown set for {cd_time} ({diff_str})"
            else:
                result_str = BOT_ERROR.COUNTDOWN_NAME_TAKEN
        except ValueError as error:
            expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
            result_str = expected + "ex. `5/17/20 @ 1:00 PM -06:00`"
            print(result_str)
        finally:
            return result_str

    def __countdown_cmd_change(self, ctx: commands.Context, cd_name: str, cd_time: str):
        result_str = ""
        try:
            pend_test_convert = pendulum.from_format(cd_time, self.pend_format) # check that the format is correct
        except ValueError as error:
            expected = "ERROR: inputted time does not match expected format `month/day/year @ hour:minute AM/PM UTC_offset`\n"
            result_str = expected + " ex. `5/17/20 @ 1:00 PM -06:00`"
            print(result_str)
            return result_str
        
        query_get_timer_by_name = f"SELECT * FROM {self.__get_cd_table_name(ctx.guild.id)} WHERE name=\'{cd_name}\';"
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            if(len(query_result) > 0):
                (query_id, query_name, query_time, query_user_id) = query_result[0]
                if(ctx.author.id == query_user_id):
                    if(self.sqlhelp.execute_update_query(self.__get_cd_table_name(ctx.guild.id), f"time=\'{cd_time}\'", f"id={query_id}")):
                        diff_str = self.__find_pend_diff_str(pend_test_convert)
                        result_str = f"Updated countdown for {cd_name}. Now set for {diff_str}"
                    else:
                        result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
                else:
                    cd_owner = ctx.guild.get_member(query_user_id)
                    result_str = BOT_ERROR.CANNOT_CHANGE_COUNTDOWN(cd_owner.name)
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)

        return result_str

    def __countdown_cmd_check(self, ctx: commands.Context, cd_name: str):
        result_str = ""
        query_get_timer_by_name = f"SELECT * FROM {self.__get_cd_table_name(ctx.guild.id)} WHERE name=\'{cd_name}\';"
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            (query_id, query_name, query_time, query_user_id) = query_result[0]
            cd_pend = pendulum.from_format(query_time, self.pend_format)
            diff_str = self.__find_pend_diff_str(cd_pend)
            result_str = f"Time until {cd_name}: {diff_str}"
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
        return result_str

    def __countdown_cmd_remove(self, ctx: commands.Context, cd_name: str):
        result_str = ""
        query_get_timer_by_name = f"SELECT * FROM {self.__get_cd_table_name(ctx.guild.id)} WHERE name=\'{cd_name}\';"
        query_result = self.sqlhelp.execute_read_query(query_get_timer_by_name)
        if(query_result != None):
            (query_id, query_name, query_time, query_user_id) = query_result[0]
            if(query_user_id == ctx.author.id):
                if(self.sqlhelp.execute_delete_query(self.__get_cd_table_name(ctx.guild.id), f"id={query_id}")):
                    result_str = f"Countdown timer `{query_name}` removed."
                else:
                    result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
            else:
                cd_owner = ctx.guild.get_member(query_user_id)
                result_str = BOT_ERROR.CANNOT_CHANGE_COUNTDOWN(cd_owner.name)
        else:
            result_str = BOT_ERROR.INVALID_COUNTDOWN_NAME(cd_name)
        return result_str

    def __countdown_cmd_list(self, ctx: commands.Context, ):
        result_str = ""
        query_get_all_timers = f"SELECT * FROM {self.__get_cd_table_name(ctx.guild.id)};"
        query_results = self.sqlhelp.execute_read_query(query_get_all_timers)
        result_str = "Countdown Name | Owner | Time | Time Until\n"
        if(query_results != None):
            for (query_id, query_name, query_time, query_user_id) in query_results:
                cd_pend = pendulum.from_format(query_time, self.pend_format) # convert to pendulum
                diff_str = self.__find_pend_diff_str(cd_pend)
                time_until_str = f"Time until {query_name}: {diff_str}"
                cd_owner = ctx.guild.get_member(query_user_id).name
                result_str += f"{query_name} | {cd_owner} | {query_time} | {time_until_str}\n"
        return result_str

    def __countdown_cmd_clean(self, ctx: commands.Context):
        result_str = ""
        query_get_all_timers = f"SELECT * FROM {self.__get_cd_table_name(ctx.guild.id)};"
        query_results = self.sqlhelp.execute_read_query(query_get_all_timers) # get all the countdowns
        if(query_results != None):
            for (query_id, query_name, query_time, query_user_id) in query_results:
                if(not pendulum.from_format(query_time, self.pend_format).is_future()): # if the countdown has passed, delete
                    result_str += f"{query_time} has passed. Deleting {query_name} countdown.\n"
                    self.sqlhelp.execute_delete_query(self.__get_cd_table_name(ctx.guild.id), f"id = {query_id}")
        return result_str

    def __find_countdown_hints(self, cd_command: str, cd_name: str, cd_time: str):
        '''
        Get argument hints based on the command input and user input - only called from SantaAdministrative.countdown()
        '''
        missing_args_str = "Missing argument(s):"
        missing_name_str = "<timer name>"
        missing_time_str = "<formatted time>"
        missing_time_hint = "Formatted time ex. `5/17/20 @ 1:00 PM -06:00`"
        complete_command_str = f"Complete command: `{CONFIG.prefix}countdown {cd_command}"
        argument_help = ""
        if(cd_command == "set"):
            if(cd_name == ""):
                argument_help = f"{missing_args_str} {missing_name_str} | {missing_time_str}\n{missing_time_hint}\n"
                argument_help += f"{complete_command_str} {missing_name_str} | {missing_time_str}`"
            elif(cd_time == ""):
                argument_help = f"{missing_args_str} {missing_time_str}\n{missing_time_hint}\n"
                argument_help += f"{complete_command_str} {cd_name} | {missing_time_str}`"
        elif(cd_command == "change"):
            if(cd_name == ""):
                argument_help = f"{missing_args_str} {missing_name_str} | {missing_time_str}\n{missing_time_hint}\n"
                argument_help += f"{complete_command_str} {missing_name_str} | {missing_time_str}`"
            elif(cd_time == ""):
                argument_help = f"{missing_args_str} {missing_time_str}\n{missing_time_hint}\n"
                argument_help += f"{complete_command_str} {cd_name} | {missing_time_str}`"
        elif(cd_command == "check"):
            if(cd_name == ""):
                argument_help = f"{missing_args_str} {missing_name_str}\n"
                argument_help += f"{complete_command_str} {missing_name_str}`"
        elif(cd_command == "remove"):
            if(cd_name == ""):
                argument_help = f"{missing_args_str} {missing_name_str}\n"
                argument_help += f"{complete_command_str} {missing_name_str}`"
        elif(cd_command == "list"):
            pass
        elif(cd_command == "clean"):
            pass
        return argument_help

    def __find_pend_diff_str(self, pend: pendulum.DateTime):
        cd_diff = pend.diff(pendulum.now())
        (diff_days, diff_hours, diff_minutes) = (cd_diff.days, cd_diff.hours, cd_diff.minutes)
        if(not pend.is_future()):
            (diff_days, diff_hours, diff_minutes) = (-diff_days, -diff_hours, -diff_minutes)
        diff_str = f"{diff_days} days, {diff_hours} hours, {diff_minutes} minutes from now"
        return diff_str

    def run_countdown_command(self, ctx: commands.Context, cd_command: str, cd_name: str, cd_time: str):
        output = self.__find_countdown_hints(cd_command, cd_name, cd_time)
        if(output == ""): # no hints were needed
            if(not self.sqlhelp.if_table_exists(self.__get_cd_table_name(ctx.guild.id))): # make sure table exists before executing the CD command
                self.sqlhelp.create_table(self.__get_cd_table_name(ctx.guild.id), "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, time TEXT NOT NULL, user_id INTEGER NOT NULL, UNIQUE(name))")
            
            if(cd_command == "set"):
                output = self.__countdown_cmd_set(ctx, cd_name, cd_time)
            elif(cd_command == "change"):
                output = self.__countdown_cmd_change(ctx, cd_name, cd_time)
            elif(cd_command == "check"):
                output = self.__countdown_cmd_check(ctx, cd_name)
            elif(cd_command == "remove"):
                output = self.__countdown_cmd_remove(ctx, cd_name)
            elif(cd_command == "list"):
                output = self.__countdown_cmd_list(ctx)
            elif(cd_command == "clean"):
                output = self.__countdown_cmd_clean(ctx)
            else:
                output = BOT_ERROR.INVALID_COUNTDOWN_COMMAND(cd_command)
                output += "\nCountdown options/sub-commands: `set`, `change`, `check` , `remove`, `list`, `clean`."

        return output