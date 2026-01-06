-- Attrition rate by Department and JobRole (BI-ready cut)
SELECT
  Department,
  JobRole,
  COUNT(*) AS employees,
  AVG(CASE WHEN LOWER(CAST(Attrition AS TEXT)) IN ('yes','1','true') THEN 1 ELSE 0 END)::float AS attrition_rate,
  AVG(MonthlyIncome)::float AS avg_monthly_income
FROM analytics.fct_employee_attrition
GROUP BY 1,2
ORDER BY attrition_rate DESC, employees DESC;
