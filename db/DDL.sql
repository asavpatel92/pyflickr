create table if not exists pyflickr (
    	id          integer primary key not null
		, username    						text
	    , image_url							text
		, latitude						  double
	    , longitude						  double
	    , isPublic						 boolean
	    , url								text
	    , title       						text
		, description       				text
		, created 	timestamp default CURRENT_TIMESTAMP
);