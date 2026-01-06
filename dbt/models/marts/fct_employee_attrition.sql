{{ config(materialized='table') }}

with base as (
  select *
  from {{ ref('stg_hr_employee') }}
)

select
  -- drop constant/identifier fields if they exist
  base.*
from base
