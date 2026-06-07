# Reconstruct a sleep diary

A lot of programs remember when recent events happened. For example, your calendar saves the start and end times for entries, and your browser cache stores the time you visited each page. You may be able to reconstruct a sleep diary by gathering up these records and assuming you were asleep during the periods where nothing happened.

!!! info "Reconstructed diaries are a rough guide"
    Every program logs activity in its own format, and access to the data is often limited for privacy reasons. That makes reconstruction technical and often inaccurate — a quick way to *see* your past pattern, not a substitute for [a proper diary](index.md).

A collection of example sources is presented below, but your best source depends on your behaviour. For example, if you're always on your Android phone, [Google Takeout](https://support.google.com/accounts/answer/3024190?hl=en) will let you download a lot of data about your activity.

## :material-file-delimited-outline: The activity-log format

To reconstruct a diary, you create an *activity log* that is then converted to a normal diary. This is a simple text file that looks something like:

```csv
maximum_day_length_ms=129600000
ActivityStart,ActivityEnd
2016-08-04T02:01:00Z,2016-08-04T04:08:16Z
12345678,23456789
... etc ...
```

- The **first line** is optional, and tells the analysis program how many milliseconds there are in the longest possible day. A 24-hour day is `86400000` ms; you only need to set this if your average day length is more than about 32 hours.
- The rest of the file uses [CSV](https://en.wikipedia.org/wiki/Comma-separated_values). The **second line** is the header (two columns: the start and end time of an activity). **Later lines** give the times for specific activities — a start time in the first column and an end in the second. If your source only specifies one time, use it in both columns.

The example shows [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) dates and [Unix time](https://en.wikipedia.org/wiki/Unix_time), but analysis programs support a wide variety of date formats. The examples below use [the dashboard](https://zeitlog.github.io/) to analyse your data — see [the ActivityLog documentation](https://github.com/zeitlog/core/tree/main/src/ActivityLog) if you want to build your own analysis software.

## :material-calendar: Calendars

Calendars store the dates and times when events occur. If you normally have events throughout your day, you can use them as an activity log:

1. export your data to [iCalendar format](https://en.wikipedia.org/wiki/ICalendar) — most calendar software can do this; search online for your program's steps
2. add the iCalendar file directly to [the dashboard](https://zeitlog.github.io/), which converts it to an activity log automatically

??? warning "Limitations of calendar data"
    Calendars can't tell the difference between being asleep and having unscheduled time. For example, if your last meeting ended at 6pm, the program will assume you went to sleep the moment it was over.

    Calendars can only record when something was *supposed* to happen. If you slept through your 8am meeting, the diary will still think you were awake.

## :material-web: Desktop browsers

Browsers store the date and time whenever you open a new page. Depending on your settings, this might be deleted after a month or so.

**Step 1 — find your history database.** Type `chrome:version` or `about:support` in the address bar; the `Profile Path` / `Profile Directory` line tells you the folder where your profile is saved. Your history database will be called `History`, `History.db` or `places.sqlite` in that folder. On macOS, press ++cmd+shift+g++ in the Finder to enter the folder name.

[The dashboard](https://zeitlog.github.io/) can create an activity log directly from your history database — you can skip step 2 if you're comfortable with that.

**Step 2 (optional) — extract the activity log by hand** with the [SQLite](https://www.sqlite.org/download.html) command-line tool (built in on macOS and Linux; install it manually on Windows). Replace `...` with the folder from step 1:

=== "Chrome / Edge"

    ```bash
    sqlite3 -csv C:\...\History '.output activity-log.chrome.csv' '.header on' \
      'SELECT visit_time/1000-11644473600000 AS ActivityStart, visit_time/1000-11644473600000 AS ActivityEnd FROM visits'
    ```

=== "Firefox"

    ```bash
    sqlite3 -csv C:\...\places.sqlite '.output activity-log.firefox.csv' '.header on' \
      'SELECT visit_date/1000 AS ActivityStart, visit_date/1000 AS ActivityEnd FROM moz_historyvisits'
    ```

=== "Safari"

    ```bash
    sqlite3 -csv C:\...\History.db '.output activity-log.safari.csv' '.header on' \
      'SELECT (visit_time+978307200)*1000 AS ActivityStart, (visit_time+978307200)*1000 AS ActivityEnd FROM history_visits'
    ```

If you see `Error: database is locked`, close your browser first. Finally, add the resulting `.csv` (or the history database itself) to [the dashboard](https://zeitlog.github.io/). You might convert the result to a spreadsheet so you can fix anything it got wrong.

??? warning "Limitations of browser data"
    Browsers can't tell the difference between being asleep and not opening new pages. For example, if you put a movie on while you fall asleep, the program assumes you fell asleep the moment the page loaded.

    They also can't tell the difference between being awake and opening new pages. If you start a playlist of sleeping music, the program assumes you were awake all night clicking through videos.

## :material-desktop-classic: Desktop operating systems

Your operating system logs when it boots up and shuts down. If you turn your computer on when you wake up and off when you go to sleep, you can use that as an activity log.

=== "Windows"

    Click `Start`, type `PowerShell` and press enter. Paste this block (right-click → paste), then press ++enter++ twice:

    ```powershell
    if ( $out_path = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)+"\activity-log.windows.csv" ) {
      write "Saving to $out_path..."
      write "ActivityStart,ActivityEnd" | Out-File -encoding ASCII -FilePath $out_path
      ForEach ( $log in Get-EventLog System ) {
        if ( $log.EventId -eq 12 ) { # powered on
           $start_time = Get-Date -Format u $log.TimeGenerated
        } elseif ( $log.EventId -eq 13 ) { # powered off
           $end_time = Get-Date -Format u $log.TimeGenerated
           write "$start_time,$end_time" | Out-File -encoding ASCII -append -FilePath $out_path
        }
      }
      write "You can close PowerShell now."
    }
    ```

    After a few seconds, `activity-log.windows.csv` appears on your desktop.

=== "Linux"

    Run this on a command line:

    ```bash
    echo 'ActivityStart,ActivityEnd' > ~/activity-log.linux.csv
    {
      sudo zcat -f /var/log/messages* /var/log/syslog*
      sudo journalctl --no-pager --system
      sudo journalctl --no-pager --user
    } \
      | grep -a '^[A-Z]' \
      | cut -c 1-12 \
      | sort -u \
      | while read REPLY
        do DATE="$( date -Iseconds -d "$REPLY:00" )"; echo "$DATE,$DATE"
        done \
      | tee -a ~/activity-log.linux.csv
    ```

    `activity-log.linux.csv` is populated in your home directory; it may take a minute or two.

Add the resulting file to [the dashboard](https://zeitlog.github.io/).

??? warning "Limitations of desktop logs"
    Desktop logs can't tell the difference between being asleep and being offline. If you turn your laptop off at 8pm, the program assumes you went to sleep then.

    They also can't tell the difference between being awake and being in use. If Windows Update keeps your computer awake until 3am, the program assumes you were too.

## :material-plus-box-outline: Other sources

Reconstruction generally means *extracting* the data from a source, *converting* it to an activity log, then *analysing* it with the diary. If you work out how to extract data from another source, [let us know](https://github.com/zeitdex/docs/issues/new?title=Reconstruct+a+diary+from+a+new+source) so we can add it here.
