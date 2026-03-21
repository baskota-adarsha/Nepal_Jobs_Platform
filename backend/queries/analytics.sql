 
 
 --top 10 most demanded skills

with skill_count as
 (SELECT  skill_id,
 count(skill_id)
  from job_skills
   group by skill_id
    order by count(skill_id) DESC LIMIT 10) 
    SELECT s.name,sc. * 
    FROM  skill_count as sc
     inner join skills s on s.id=sc.skill_id ;



     ---avg salary by district

SELECT district,
avg(salary_min) as avg_salary_min,
avg(salary_max) as avg_salary_max
 from jobs
 where  salary_min is not null and salary_max is not null
 group by district
  order by avg(salary_min) desc, avg(salary_max) desc;

--(3) jobs posted per month last 6 months, 

SELECT
 EXTRACT(YEAR FROM posted_at) AS year, 
EXTRACT (MONTH FROM posted_at) AS month,
COUNT(id) AS job_count
from jobs 
where posted_at > CURRENT_DATE - INTERVAL '6 Months'
GROUP BY EXTRACT(YEAR FROM posted_at), EXTRACT(MONTH FROM posted_at)
ORDER BY EXTRACT(YEAR FROM posted_at) DESC, EXTRACT(MONTH FROM posted_at) DESC;




---companies with most active listing

WITH postings_count as (
SELECT 
company_id,
COUNT(id) num_active_postings
from jobs
where is_active is true 
group by company_id
ORDER BY COUNT(id) desc)
select c.name,p.* from postings_count p left join companies c on c.id=p.company_id ORDER BY p.num_active_postings desc ;


--- skills demand by category.
WITH skill_count AS (
    SELECT skill_id, COUNT(skill_id) AS skill_count
    FROM job_skills
    GROUP BY skill_id
),
skill_with_details AS (
    SELECT sc.skill_id, sc.skill_count, s.name, s.category
    FROM skill_count sc
    INNER JOIN skills s ON s.id = sc.skill_id
)
SELECT category, SUM(skill_count) AS num_job_postings
FROM skill_with_details
GROUP BY category
ORDER BY num_job_postings DESC;


