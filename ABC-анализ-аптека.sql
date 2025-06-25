-- Создаём временную таблицу по товарам
with abc_sales as (
    select
        dr_ndrugs as product, -- название или код лекарства
        sum(dr_kol) as amount, -- общее количество продаж
        sum(dr_kol*(dr_croz - dr_czak) - dr_sdisc) as profit, -- общая прибыль: объём * (розничная цена - закупочная) минус скидки
        sum(dr_kol*dr_croz - dr_sdisc) as revenue -- общая выручка: объём * розничная цена минус скидки
    from sales s
    group by dr_ndrugs -- группировка по продукту
)


–классификация по ABC-анализу
select
    s.product,


    -- ABC по количеству (amount)
    case
        when sum(amount) over(order by amount desc) / sum(amount) over() <= 0.8 then 'A' -- топ 80% объёма
        when sum(amount) over(order by amount desc) / sum(amount) over() <= 0.95 then 'B' -- следующие 15%
        else 'C' -- оставшиеся 5%
    end amount_ABC,


    -- ABC по прибыли
    case
        when sum(profit) over(order by profit desc) / sum(profit) over() <= 0.8 then 'A'
        when sum(profit) over(order by profit desc) / sum(profit) over() <= 0.95 then 'B'
        else 'C'
    end profit_ABC,


    -- ABC по выручке
    case
        when sum(revenue) over(order by revenue desc) / sum(revenue) over() <= 0.8 then 'A'
        when sum(revenue) over(order by revenue desc) / sum(revenue) over() <= 0.95 then 'B'
        else 'C'
    end revenue_ABC


from abc_sales s
order by product -- сортировка по названию продукта