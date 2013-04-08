#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime
import re
import threading

import sublime
import sublime_plugin

settings = sublime.load_settings('clmemo.sublime-settings')

class SublimeClemoCommon():
    def __init__(self):
        self.open_tasks_bullet = settings.get('open_tasks_bullet')
        self.done_tasks_bullet = settings.get('done_tasks_bullet')
        self.canc_tasks_bullet = settings.get('canc_tasks_bullet')
        self.changelog_path = settings.get('changelog_path')
        self.user_name = settings.get('user_name')
        self.mail_address = settings.get('mail_address')
        self.max_move_entry = settings.get('max_move_entry')
        self.titles = settings.get('titles')
        self.max_move_entry = settings.get('max_move_entry')

    def insert_entry_header(self, view, edit):
        now_date = datetime.date.today()
        now_date = now_date.strftime('%Y-%m-%d')
        date_region = view.find('^' + now_date, 0)

        begin = 0
        if date_region == None:
            view.insert(edit, 0, '\n')
            view.insert(edit, 0, self.create_entery_header(now_date) + '\n')

    def create_entery_header(self, now_date):
        return now_date + '  ' + self.user_name + '  ' + '<'+self.mail_address+'>'

    def insert_title(self, view, edit, title):
        begin = view.text_point(1, 0)
        view.insert(edit, begin, '\n')
        begin = view.text_point(2, 0)

        if title[len(title)-1] == '\n':
            view.insert(edit, begin, title)
        else:
            view.insert(edit, begin, title + '\n')

        # 入力したタイトルの後ろのpositionを返す
        return begin + len(title)

    def title_rapping(self, title):
        return '\t* ' + title + ': '

class SublimeClmemoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.cl = SublimeClemoCommon()
        if not os.path.exists(self.cl.changelog_path):
            return

        changlog_view = sublime.active_window().open_file(self.cl.changelog_path)
        changlog_view.set_syntax_file('Packages/SublimeClmemo/clmemo.tmLanguage')
        sublime.active_window().show_quick_panel(self.cl.titles, self.on_done)

    def on_done(self, index):
        if index == -1 :
            title = None
        else:
            title = self.cl.titles[index]
        sublime.active_window().run_command('sublime_clmemo_core', {'title': title})


class SublimeClmemoCore(sublime_plugin.TextCommand):
    def run(self, edit, title):
        if title == None:
            return

        cl = SublimeClemoCommon()
        cl.insert_entry_header(self.view, edit)
        end = cl.insert_title(self.view, edit, cl.title_rapping(title))

        pt = sublime.Region(end, end)
        self.view.sel().clear()
        self.view.sel().add(pt)
        self.view.show(pt)


class TaskNewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cl = SublimeClemoCommon()
        for region in self.view.sel():
            line = self.view.line(region)
            line_contents = self.view.substr(line).rstrip()
            has_bullet = re.match('^(\s*)[' + re.escape(cl.open_tasks_bullet) + re.escape(cl.done_tasks_bullet) + re.escape(cl.canc_tasks_bullet) + ']', self.view.substr(line))
            current_scope = self.view.scope_name(self.view.sel()[0].b)
            if has_bullet:
                grps = has_bullet.groups()
                line_contents = self.view.substr(line) + '\n' + grps[0] + cl.open_tasks_bullet + ' '
                self.view.replace(edit, line, line_contents)
            elif 'header' in current_scope:
                header = re.match('^(\s*)\S+', self.view.substr(line))
                if header:
                    grps = header.groups()
                    line_contents = self.view.substr(line) + '\n' + grps[0] + ' ' + cl.open_tasks_bullet + ' '
                else:
                    line_contents = ' ' + cl.open_tasks_bullet + ' '
                self.view.replace(edit, line, line_contents)
                end = self.view.sel()[0].b
                pt = sublime.Region(end, end)
                self.view.sel().clear()
                self.view.sel().add(pt)
            else:
                has_space = re.match('^(\s+)(.*)', self.view.substr(line))
                if has_space:
                    grps = has_space.groups()
                    spaces = grps[0]
                    line_contents = spaces + cl.open_tasks_bullet + ' ' + grps[1]
                    self.view.replace(edit, line, line_contents)
                else:
                    line_contents = ' ' + cl.open_tasks_bullet + ' ' + self.view.substr(line)
                    self.view.replace(edit, line, line_contents)
                    end = self.view.sel()[0].b
                    pt = sublime.Region(end, end)
                    self.view.sel().clear()
                    self.view.sel().add(pt)

class TaskCompleteCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cl = SublimeClemoCommon()
        original = [r for r in self.view.sel()]
        for region in self.view.sel():
            line = self.view.line(region)
            line_contents = self.view.substr(line).rstrip()
            rom = '^(\s*)' + re.escape(cl.open_tasks_bullet) + '\s*(.*)$'
            rdm = '^(\s*)' + re.escape(cl.done_tasks_bullet) + '\s*(.*)$'
            rcm = '^(\s*)' + re.escape(cl.canc_tasks_bullet) + '\s*(.*)$'
            open_matches = re.match(rom, line_contents)
            done_matches = re.match(rdm, line_contents)
            canc_matches = re.match(rcm, line_contents)
            if open_matches:
                grps = open_matches.groups()
                replacement = u'%s%s %s' % (grps[0], cl.done_tasks_bullet, grps[1].rstrip())
                self.view.replace(edit, line, replacement)
            elif done_matches:
                grps = done_matches.groups()
                replacement = u'%s%s %s' % (grps[0], cl.open_tasks_bullet, grps[1].rstrip())
                self.view.replace(edit, line, replacement)
            elif canc_matches:
                grps = canc_matches.groups()
                replacement = u'%s%s %s' % (grps[0], cl.done_tasks_bullet, grps[1].rstrip())
                self.view.replace(edit, line, replacement)
        self.view.sel().clear()
        for ind, pt in enumerate(original):
            new_pt = sublime.Region(pt.a, pt.b)
            self.view.sel().add(new_pt)


class TaskCancelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        cl = SublimeClemoCommon()
        original = [r for r in self.view.sel()]
        for region in self.view.sel():
            line = self.view.line(region)
            line_contents = self.view.substr(line).rstrip()
            rom = '^(\s*)' + re.escape(cl.open_tasks_bullet) + '\s*(.*)$'
            rdm = '^(\s*)' + re.escape(cl.done_tasks_bullet) + '\s*(.*)$'
            rcm = '^(\s*)' + re.escape(cl.canc_tasks_bullet) + '\s*(.*)$'
            open_matches = re.match(rom, line_contents)
            done_matches = re.match(rdm, line_contents)
            canc_matches = re.match(rcm, line_contents)
            if open_matches:
                grps = open_matches.groups()
                replacement = u'%s%s %s' % (grps[0], cl.canc_tasks_bullet, grps[1].rstrip())
                self.view.replace(edit, line, replacement)
            elif done_matches:
                pass
            elif canc_matches:
                grps = canc_matches.groups()
                replacement = u'%s%s %s' % (grps[0], cl.open_tasks_bullet, grps[1].rstrip())
                self.view.replace(edit, line, replacement)
        self.view.sel().clear()
        for ind, pt in enumerate(original):
            new_pt = sublime.Region(pt.a, pt.b)
            self.view.sel().add(new_pt)


class TaskMovedToTodayCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.cl = SublimeClemoCommon()
        self.cl.insert_entry_header(self.view, edit)
        open_tasks = self.get_open_tasks()
        if len(open_tasks) == 0:
            print 'open_tasks == nothing'
            return

        # for a in open_tasks:
        #     for b in a.items:
        #         print a.entry_date
        #         print b
        # return
        # 上から順番にタスクを消すと下のタスクのregionが変わるので下から順番に消す
        parent_pattern = re.compile(u'%s.*:$' % self.cl.open_tasks_bullet)
        child_pattern = re.compile(u'^\t\s')
        # tree_match = re.serch(u'(^\s.*%s.*:.*\s(^\t\s.*\s)*)' % self.cl.open_tasks_bullet)
        parent_index = 0

        for task in reversed(open_tasks):
            title_group_string = self.view.substr(task.title_group_region)

            for item_region in reversed(task.items_region):
                m = parent_pattern.search(self.view.substr(item_region))
                if m != None:
                    
                    parent_string = self.view.substr(sublime.Region(item_region.begin()+3, item_region.end()-1))
                    pare_m = re.search(u'(^\s.*%s.%s:\s(^\t\s.*\s)*)' % (self.cl.open_tasks_bullet, parent_string), title_group_string, re.M)
                    if self.cl.done_tasks_bullet in pare_m.group(1) or \
                       self.cl.canc_tasks_bullet in pare_m.group(1):
                       open_task_region = sublime.Region(item_region.begin()+m.start(), item_region.begin()+m.start()+1)
                       self.view.replace(edit, open_task_region, u'■')
                    else:
                        self.view.erase(edit, self.view.full_line(item_region))
                else:
                    self.view.erase(edit, self.view.full_line(item_region))

            # タイトルがすべて未完タスクだったらタイトルヘッダも削除（タイトル内の全てのタスクが無くなる為）
            has_except_done = False
            if self.cl.done_tasks_bullet in title_group_string or \
               self.cl.canc_tasks_bullet in title_group_string:
                has_except_done = True

            if  not has_except_done:
                # region.endを+1して、タイトル区切り用の改行も削除する
                del_title_header_region = \
                    sublime.Region(task.title_header_region.begin(), task.title_header_region.end()+1)
                self.view.erase(edit, self.view.full_line(del_title_header_region))

        # create inserting tasks
        title_groups = []
        i = 0
        for task in open_tasks:
            title_groups.append(task.title_header + '\n')
            for item in task.items:
                # 階層の親は差分の日にち無し
                if None != parent_pattern.search(item):
                    title_groups[i] += item + '\n'
                    continue

                # タスクの後ろに何日経ったか差分の日を入力
                diff_day = datetime.date.today() - task.entry_date
                diffed_day = 0
                m = re.search(u'(\+)(\d+)$', item)
                if m != None:
                    diffed_day = int(m.groups()[1])
                    diff_day = diff_day + datetime.timedelta(days=diffed_day)
                    item = re.sub(u'\s\+\d+$', '', item)
                title_groups[i] += item + u' +' + str(diff_day.days) + '\n'
            i += 1

        # insert tasks
        # スタックみたいに先頭データが下に行ってしまうのでreversedする
        for group in reversed(title_groups):
            self.cl.insert_title(self.view, edit, group)

    def get_open_tasks(self):
        entry_regions = self.view.find_all('^\d{4}.\d{2}.\d{2}')
        entry_regions.append(sublime.Region(self.view.size(), self.view.size()))  # sentinel
        try:
            first_entry_date = datetime.datetime.strptime(self.view.substr(entry_regions[0]), '%Y-%m-%d')
            first_entry_date = datetime.date(first_entry_date.year, first_entry_date.month, first_entry_date.day)
            if first_entry_date == datetime.date.today():
                del entry_regions[0]
                if len(entry_regions) == 0:
                    return []
        except Exception, e:
            return []

        title_group_regions = self.view.find_all('(^\t\*.*?:.*\s(^\t.*\s)*)')
        title_index = 0
        open_tasks = []

        for entry_index in range(len(entry_regions) - 1):
            if int(self.cl.max_move_entry) <= entry_index:
                break

            entry_begin = entry_regions[entry_index].begin()
            entry_end =   entry_regions[entry_index+1].begin()

            # entryの中からtitle検索
            while 1:
                title_group_region = title_group_regions[title_index]
                if entry_begin > title_group_region.begin():
                    # 本日のタスクなので処理せず
                    title_index += 1
                    continue

                if title_group_region.begin() > entry_end:
                    break

                # titleの中からitem検索
                rom = u'^\s*%s.*$' % self.cl.open_tasks_bullet
                item_region = self.view.find(rom, title_group_region.begin())
                is_first = True

                while item_region and (item_region.begin() < title_group_region.end()):
                    if is_first == True:
                        open_task = title_group(self.view)
                        open_task.set_entry_date(self.view.substr(entry_regions[entry_index]))
                        open_task.set_title_group_region(title_group_region)
                        open_tasks.append(open_task)
                        is_first = False
                    open_task.set_item_region(item_region)
                    item_region = self.view.find(rom, item_region.end() + 1)

                title_index += 1

        return open_tasks


class SublimeClmemoGrepCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('Grep Word', '', self.on_done, None, None)

    def on_done(self, find_word):
        sublime.active_window().run_command('sublime_clmemo_grep_core', {'find_word': find_word})


class SublimeClmemoGrepCore(sublime_plugin.TextCommand):
    def run(self, edit, find_word):
        cl = SublimeClemoCommon()
        title_group = re.compile(u'(\t\*.*?:.*\s(\t.*\s)*)')
        all_regions = self.view.find_all('((^\d.+\n\n)(^\t\*.*?:.*\s(^\t.*\s)*\n)*)')

        grep_view = sublime.active_window().new_file()
        grep_view.set_syntax_file('Packages/SublimeClmemo/clmemo.tmLanguage')

        sublime.set_timeout(lambda: self.ResultWriteThread(edit, find_word, title_group, all_regions, self.view, grep_view), 0)

    def ResultWriteThread(self, edit, find_word, title_group, all_regions, clmemo_view, grep_view):
        find_entries = []

        # 上にどんどん検索結果を積んで行きたいので、古い日付のものから調べていく
        for region in reversed(all_regions):
            entry_header = clmemo_view.substr(clmemo_view.full_line(region.begin())) + '\n'
            find_entry = entry_header
            is_in = False

            has_title_groups = title_group.finditer(clmemo_view.substr(region), re.M)
            for m in has_title_groups:
                has_find_word = re.search('.*%s.*' % re.escape(find_word), m.group(), re.M)
                if not has_find_word:
                    continue

                is_in = True
                find_entry += m.group() + '\n'

            if is_in:
                find_entries.append(find_entry)

        for find_entry in find_entries:
            grep_view.insert(edit, 0, find_entry)

        # 見た目が似てるので間違えて編集しないように
        grep_view.set_read_only(True)


class title_group():
    def __init__(self, view):
        self.view = view
        self.__items_region = []
        self.__items = []

    def set_entry_date(self, entry_date):
        if isinstance(entry_date, unicode) == True:
            entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d')
            self.__entry_date = datetime.date(entry_date.year, entry_date.month, entry_date.day)
        else:
            self.__entry_date = entry_date

    def set_entry_region(self, region):
        self.__entry_region = region
        self.__entry_header = self.view.substr(region)

    def set_title_group_region(self, region):
        self.__title_group_region = region
        self.__title_header_region = self.view.line(region.begin())
        self.__title_header = self.view.substr(self.title_header_region)

    def set_item_region(self, region):
        self.__items_region.append(region)
        self.__items.append(self.view.substr(region))

    @property
    def entry_date(self):
        return self.__entry_date

    @property
    def title_group_region(self):
        return self.__title_group_region

    @property
    def title_header_region(self):
        return self.__title_header_region

    @property
    def title_header(self):
        return self.__title_header

    @property
    def items_region(self):
        return self.__items_region

    @property
    def items(self):
        return self.__items

