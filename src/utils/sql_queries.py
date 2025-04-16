listings_table_sql = ('SELECT  url, Price, Area,'
                      ' Rooms, Floor, "Max Floor",'
                      ' GoToLink, ReportDate, add_date, is_active'
                      ' FROM listings WHERE is_active = 1')

new_listings_table_sql = ('SELECT  url, Price, Area,'
                      ' Rooms, Floor, "Max Floor",'
                      ' GoToLink, ReportDate, add_date, is_active'
                      ' FROM new_listings WHERE is_active = 1')