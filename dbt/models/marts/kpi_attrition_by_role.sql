{{ config(materialized='table') }}

with base as (
  select *
  from {{ ref('fct_employee_attrition') }}
),
labeled as (
  select
    *,
    case when lower(cast(attrition as {{ dbt.type_string() }})) in ('yes','1','true') then 1 else 0 end as attrition_flag
  from base
)

select
  department,
  jobrole,
  count(*) as employees,
  avg(attrition_flag)::float as attrition_rate,
  avg(monthlyincome)::float as avg_income
from labeled
group by 1,2
order by attrition_rate desc, employees desc
