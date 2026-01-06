# dbt models (Postgres)

This repo includes a small dbt project to demonstrate analytics engineering patterns (staging → marts, tests, docs).

## Run locally
1. Start Postgres via docker-compose at the repo root.
2. Load data into `raw.hr_employee` using `make seed-db`.
3. Configure your dbt profile (example below).
4. Run:
   - `dbt deps`
   - `dbt seed` (not required here)
   - `dbt run`
   - `dbt test`
   - `dbt docs generate`

### Example `profiles.yml`
Create `~/.dbt/profiles.yml`:

```yaml
ibm_hr_attrition:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: postgres
      password: postgres
      port: 5432
      dbname: hr_analytics
      schema: public
```
