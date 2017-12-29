select t.*, al.Title
from Track t
left join Album al on al.AlbumId = t.AlbumId
where
 (:Name = '' or t.Name like '%' || :Name || '%')
 and (:AlbumId = '' or t.AlbumId = :AlbumId)
