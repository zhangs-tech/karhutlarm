# Test Scenarios

## Test documentation

Screenshots and recordings of the tests: [Google Drive folder](https://drive.google.com/drive/folders/1KcEVUtFTR_B8xb9fkLskz6jKMmTBOkxJ?usp=sharing)

Result: all 7 test cases passed and matched the expected result.

## Status rules (from `get_status()`)

| Condition | Test used by the code |
|---|---|
| smoke | `gas > 3830` (raw ADC, strictly greater) |
| high temperature | `temp > 50.0` (strictly greater) |
| low humidity | `humidity < 40.0` (strictly less) |

| Result | Rule | Serial code | RGB LED (common anode) | Buzzer | Dashboard badge |
|---|---|---|---|---|---|
| DANGER | high temperature, or (smoke and low humidity) | 2 | red only | 2000 Hz tone | red |
| WARNING | smoke, or low humidity (and not DANGER) | 1 | red and green (yellow) | off | yellow |
| NORMAL | none of the conditions | 0 | green only | off | green |


## Test cases

In every case, the Wokwi DHT22 and gas sensor are set by clicking the part.
The firmware reads the sensors and publishes one reading about every second.

| ID | Test Case | Input / Condition | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| T1 | Normal conditions | Temp 28 °C, humidity 70 %, gas below 3830 | Serial `Status: 0`. LED green. Buzzer off. Badge `NORMAL` (green). | Matches the expected result. | Pass |
| T2 | Smoke only | Temp 28 °C, humidity 70 %, gas above 3830 | Serial `Status: 1`. LED yellow. Buzzer off. Badge `WARNING` (yellow). | Matches the expected result. | Pass |
| T3 | Dry air only | Temp 28 °C, humidity 30 %, gas below 3830 | Serial `Status: 1`. LED yellow. Buzzer off. Badge `WARNING` (yellow). | Matches the expected result. | Pass |
| T4 | Smoke and dry air | Temp 28 °C, humidity 30 %, gas above 3830 | Serial `Status: 2`. LED red. Buzzer sounds. Badge `DANGER` (red). | Matches the expected result. | Pass |
| T5 | High temperature | Temp 55 °C, humidity 70 %, gas below 3830 | Serial `Status: 2`. LED red. Buzzer sounds. Badge `DANGER` (red). | Matches the expected result. | Pass |
| T6 | Recovery | After T4 or T5, set the T1 values | Serial `Status: 0`. LED green. Buzzer stops. "Status changes" list shows `NORMAL` above `DANGER` (newest first). | Matches the expected result. | Pass |
| T7 | Offline detection | With the dashboard open, stop the Wokwi simulation and wait 15 seconds | Badge turns gray and shows `OFFLINE (<last status>)`. "Last reading Ns ago" keeps counting up.| Pass |


## Gas sensor note

The threshold is a raw ADC value (3830). The ADC range is 0 to 4095.
The Wokwi gas sensor slider is in ppm.
Move the slider until the Serial `Gas:` value is above or below 3830.
Write the slider position in the "Input / Condition" column.

## Known limits

- If the DHT22 read fails, the firmware sets temperature and humidity to 0 for that cycle.
  A humidity of 0 is below 40, so the status shows WARNING. This is not one of the tests above.
- The dashboard shows the last 300 readings on the chart and the last 10 status changes.
