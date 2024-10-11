# lilsched
Little scheduler

## Usage
1. Create a data file such as the sample `data.toml`
     - Must have a structure of `students.<name>.slots` where each slot has the format `{ weekday = "Mon/Tue/Wed/Thu/Fri/Sat/Sun", slot = 13.5 }` (`13.5` means 13:30, `16` means 16:00, 24h clock)
2. Run `python3 lilsched.py data.toml`
      - Optionally add `-n 4` to change the amount of time slots needed
3. You're set.
