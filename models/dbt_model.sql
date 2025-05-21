/*
    BenBox Starter dbt Model
    This is a sample model for the BenBox dbt project.
    You can configure models directly within SQL files.
    The config below will override settings in dbt_project.yml.
*/

{{ config(materialized='view') }}

with source_data as (

    select 1 as id
    union all
    select null as id

)

select *
from source_data

-- Uncomment the line below to remove records with null `id` values
-- where id is not null
/*
    Uncomment the line below to remove records with null `id` values
*/

-- where id is not null
