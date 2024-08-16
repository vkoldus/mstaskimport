# MS Task import

This tool reads CSV files exported from TODOist and then uses MS Graph API to import the task lists into Microsoft TODO app.

The tool was written in a weekend for personal use and the author doesn't guarantee any features or consistency of data.

It can also serve as a simple example how to interact directly with the MS Graph API. It took me a few hours to figure out, maybe reading this code can save you some time if that's what you want to do.

## Limitations

Only task titles and descriptions are imported.

Only one level of nesting is supported. Subtasks are imported as checklist items.

Dates, priorities and other data is ignored but support can be added relatively easily. Merge requests are welcome.

There is no unit tests or quality control. No data sanitization or robust error checking. Bugs are very possible. The tool worked fine for my few personal lists I needed to migrate, but is far from general release quality. USE IT AT YOUR OWN RISK.

## How to run

You cannot run the tool from the source code out of the box, because I'm not disclosing my Graph API client id for this app in the code. You can register the app under your own account and put it there. Then you can install poetry and run simply with:

> poetry install

> poetry run mstaskimport

I will try to provide binaries with my client id so more people can use the tool, but no promises.

## Licensing

The source code is licensed under GPL v3. License is available [here](./LICENSE).
