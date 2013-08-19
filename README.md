## 概要

Emacsの[clmemo](http://www.bookshelf.jp/texi/clmemo/clmemo.html)っぽいことをSublime TextでできるようにするPluginです
[ここ](https://github.com/shibainurou/SublimeClmemo)からPakagesにcloneしてください

__使いかた__

* __SublimeClmemo用ファイルを作る__
ファイルの場所はどこでも好きなところで

* __設定ファイルの `changelog_path` を変更する__
さっき作ったSublimeClmemo用ファイルのパス設定

* __設定ファイルの `user_name`, `mail_address` を変更する__
自分の名前とメールアドレスを設定
この二つはヘッダ為だけに使うので適当でいいです

* __設定ファイルの `titles` を変更する__
よく使うタイトルをカンマ区切りで複数設定します
例）"titles": ["todo", "daiary", "python", "idea", "buy", "pay"],

* __使ってみる__
`ctrl(super)+shift+l` 押下して、タイトルを決定する
好きなことを、書くべし書くべし


* __タスク機能使ってみる__
`ctrl(super)+i` タスクを作成
`ctrl(super)+t` タスク完了
`ctrl(super)+m` タスクキャンセル

## 書式

```
2013-03-25  user_name  <mail@address.com>

	* タイトル[カテゴリー]: タイトルヘッダ
	アイテム
	アイテム

	* Title: タイトルヘッダ
	☐ todo
	✘ キャンセルしたtodo
	✔ 完了したtodo
	☐ todo_parent:
	 ☐ todo_child1
	 ☐ todo_child2

```

行頭には`tab`
改行のみのアイテムを作らない
親todoの後ろに `:` をつける
子todoは親よりもスペース一個分後ろにさげる
ファイルの一番最後は改行を入れる

## 機能

__ChangeLogを開いてタイトルを挿入する__
`key` : ctrl(super)+shift+l
`command` : sublime_clmemo

__タスクを現在の日付に集める__
`key` : f1
`command` : task_moved_to_today

__ChangeLogをgrepする__
`key` : f2
`command` : sublime_clmemo_grep

__タスク(☐)を挿入する__
`key` : ctrl+i
`command` : task_new

__タスク(☐)を完了(✔)にする__
`key` : ctrl+t
`command` : task_complete

__タスク(☐)をキャンセル(✘)にする__
`key` : ctrl+m
`command` : task_cancel

## 設定

__open_tasks_bullet__
未完了todoのマークを選択する

__done_tasks_bullet__
完了todoのマークを選択する

__canc_tasks_bullet__
キャンセルtodoのマークを選択する

__changelog_path__
ChangeLogのpath

__user_name__
user name

__mail_address__
mail address

__max_move_entry__
todoを今日の日付に移動させる時、何個下のエントリーまで遡って移動させるかを設定する

__titles__
よく使うタイトルを設定する

__`changelog_path` `user_name` `mail_address` `titles` は設定しておいてください。__
