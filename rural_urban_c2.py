import datetime
from google.cloud import bigquery
# from matplotlib.pyplot import plot_date, axis, show, gcf, bar
import matplotlib.pyplot as plt


def get_data():

    sql_u = """
        select
            t3.date,
            t3.state,
            t3.ru_code,
            t3.daily_cases,
            t3.daily_deaths,
            --round(t3.daily_cases/t3.population *100000,2) as daily_cases_per_100k_people,
            --round(t3.daily_deaths/t3.population *100000,2) as daily_deaths_per_100k_people

    from(

    select t1.date, t1.state, t1.ru_code,
          t1.cases, t1.cases - lag(t1.cases) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_cases,
          t1.deaths,t1.deaths - lag(t1.deaths) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_deaths,
          t2.population
    from
    (select c.date, c.state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code,
           sum(c.cases) as cases, sum(c.deaths) as deaths
    from covid19.us_counties as c
    join covid19.rural_urban_codes_2013 ruc
       on ruc.FIPS = c.fips
    group by c.date, c.state, ru_code
    order by c.state, ru_code, c.date) as t1
    join covid19.state_conversion as sc
       on sc.state_long = t1.state
    join
    (
    select state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code, sum(population_2010) as population
    from covid19.rural_urban_codes_2013 as ruc
    group by state, ru_code
    ) as t2
       on t2.state = sc.state_code
    where t1.ru_code = t2.ru_code
    and t1.state = 'Washington'
    order by state, ru_code, date
    ) t3
    where ru_code = 'U'

    order by state, ru_code, date;
"""

    sql_r = """
        select
            t3.date,
            t3.state,
            t3.ru_code,
            t3.daily_cases,
            t3.daily_deaths,
            --round(t3.daily_cases/t3.population *100000,2) as daily_cases_per_100k_people,
            --round(t3.daily_deaths/t3.population *100000,2) as daily_deaths_per_100k_people

    from(

    select t1.date, t1.state, t1.ru_code,
          t1.cases, t1.cases - lag(t1.cases) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_cases,
          t1.deaths,t1.deaths - lag(t1.deaths) over(partition by t1.state, t1.ru_code order by t1.date) as  daily_deaths,
          t2.population
    from
    (select c.date, c.state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code,
           sum(c.cases) as cases, sum(c.deaths) as deaths
    from covid19.us_counties as c
    join covid19.rural_urban_codes_2013 ruc
       on ruc.FIPS = c.fips
    group by c.date, c.state, ru_code
    order by c.state, ru_code, c.date) as t1
    join covid19.state_conversion as sc
       on sc.state_long = t1.state
    join
    (
    select state, case when ruc.rucc_2013 <= 3 then 'U' else 'R' end as ru_code, sum(population_2010) as population
    from covid19.rural_urban_codes_2013 as ruc
    group by state, ru_code
    ) as t2
       on t2.state = sc.state_code
    where t1.ru_code = t2.ru_code
    and t1.state = 'Washington'
    order by state, ru_code, date
    ) t3
    where ru_code = 'R'

    order by state, ru_code, date;
"""

    client = bigquery.Client(project='paul-henry-tremblay')
    result_u = client.query(sql_u)
    final_u = []
    for i in result_u:
        date = i.get('date')
        daily_cases = i.get('daily_cases')
        final_u.append([date, daily_cases])

    result_r = client.query(sql_r)
    final_r = []
    for i in result_r:
        date = i.get('date')
        daily_cases = i.get('daily_cases')
        final_r.append([date, daily_cases])
    return (final_u, final_r)


def daily_cases_graph(dates_1, val_1, dates_2, val_2):
    # plot_date(dates, daily_cases, "o", color="blue", markeredgecolor="black")
    plt.plot(dates_1, val_1, linewidth=2.0)
    plt.plot(dates_2, val_2, linewidth=2.0)
    plt.title('Rural vs Urban daily cases in Washington State')
    #plt.dates('date')
    #plt.daily_cases('daily cases')
    #plt.setp(lines, color='r', linewidth=2.0)
    # figure(figsize=(20, 10))
    plt.gcf().autofmt_xdate()
    plt.show()


sd_u, sd_r = get_data()
dates_1 = [i[0] for i in sd_u]
val_1 = [i[1] for i in sd_u]

dates_2 = [i[0] for i in sd_r]
val_2 = [i[1] for i in sd_r]
print(dates_1)
print()
print(val_1)
print()
print(dates_2)
print()
print(val_2)
daily_cases_graph(dates_1, val_1, dates_2, val_2)
