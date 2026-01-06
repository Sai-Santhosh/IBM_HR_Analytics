{{ config(materialized='view') }}

select
  *
from {{ source('raw', 'hr_employee') }}
