SET @num = 3;

SET sql_mode = '';

select distinct res_set.gr from (
select count(*) as gr_count, hash as gr, tag as gr_tag
from tags
where type = 'label' and find_in_set(tag, 'product,fun,red')
group by gr
having gr_count = @num) as res_set


