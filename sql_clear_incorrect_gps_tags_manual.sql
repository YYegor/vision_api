SELECT * FROM vision_api.tags where tag_value='GPS Country';

start TRANSACTION;
SET sql_mode = '';
DROP TABLE IF EXISTS t;
CREATE TEMPORARY TABLE t (id int);

insert into t (id) 
SELECT id FROM vision_api.tags where tag_value='GPS Country';

update vision_api.tags set tag_value='Russia', tag='GPS Country', type='meta' where id in (SELECT id from t) ;

commit;


