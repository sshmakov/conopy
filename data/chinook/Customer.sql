select cu.*, em.FirstName || ' ' || em.LastName 'Employee Name'
from Customer cu
left join Employee em on em.EmployeeId = cu.SupportRepId
where 
  (:CustomerId = '' or cu.CustomerId = :CustomerId)
  and (:EmployeeId = '' or cu.SupportRepId = :EmployeeId)
