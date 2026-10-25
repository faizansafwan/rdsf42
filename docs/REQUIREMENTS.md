# Original Requirements (from the product manager)

Problem setting: you are a product developer developing and delivering a customized
software product to a client. A product manager has given the context, directions, and
requirements below. Understand it, do additional learning and information gathering to
gain sufficient domain knowledge, then develop the first version of the product based on
it. You also need to:

- present and pitch the product to the client
- explain the software design and implementation to an internal technical lead
  reviewing the work

## Requirement

The client is an energy utility in the UK. They need to buy electricity from the
wholesale market to serve their consumers. The specific team (that we are pitching the
software to) is responsible for buying required power from the UK day-ahead market. More
specifically, to meet their consumers' electricity demand, they need to understand how
much power needs to be additionally procured (e.g., from thermal plants) beyond the
generation available from renewable sources like wind. The power generation from
renewable sources is weather-dependent, and the power purchase decisions from the
day-ahead market need to be made one day before the delivery day. Hence, they need to
rely on renewable generation forecasts when making decisions.

Using the web app, they need to:

1. Clearly understand the latest renewable generation forecasts available when they
   need to make decisions on buying from the day-ahead market.
2. Evaluate the accuracy of the renewable generation forecasts quantitatively, so that
   they can make their decisions considering the quantified error.

To limit scope, for the above two purposes, only national-level actual and forecasted
wind power from Elexon is considered (no other data beyond this).

### Actual generation
Available at
`https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream`. Consider
values where `"fuelType"` is `"WIND"`. Relevant fields:
- `"startTime"`: the target time (resolution of 30 minutes)
- `"generation"`: generated wind power

### Forecasted generation
Available at
`https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream`. Relevant
fields:
- `"startTime"`: similar to `startTime` in the actuals dataset
- `"publishTime"`: the time at which the forecast was created
- `"generation"`: similar to `generation` in the actuals dataset

Only data relevant to purchase decisions made in **January 2026**.

Build the application using **React** for front-end and **Python** for backend. AI
tools may be used to assist (mention this explicitly in the README). Use **Docker**.
Deploy to **Vercel or Heroku**.

**Do not spend more than 16 hours on this assignment.**

## Deliverables

### Video demo
Unlisted YouTube video, two parts, max 10 minutes total:
- **Part 1** (≤5 min): present and pitch the portal/analysis to the customer as pilot
  project output — the goal is to impress them.
- **Part 2** (≤5 min): show the work to the tech lead for review — explain
  architecture, design, analysis, code base, and key development practices; make review
  easy and provide clear knowledge transfer.

Evaluation starts with the video — don't submit without it.

### Repo
Public GitHub repo with an anonymous repo name (random string, e.g. "kjhwr"). README
must contain:
- Details of the files and directories present
- How to start the application
- Link to the deployed Vercel/Heroku app

### Submission form
Submit all details via the submission form. Open every submitted URL in incognito mode
first and verify sufficient access is available.
