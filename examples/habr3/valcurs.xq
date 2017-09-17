xquery version "1.0" encoding "utf-8";
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  </head>
  <body>
    <div>Курсы ЦБ на {string(/ValCurs/@Date)}</div>
    <table><tbody>
      <tr>
        <th>Код валюты</th>
        <th>Код валюты</th>
        <th>Номинал</th>
        <th>Название</th>
        <th>Курс</th>
      </tr>
    {for $i in /ValCurs/Valute
    return (
      <tr>
        <td>{string($i/NumCode)}</td>
        <td>{string($i/CharCode)}</td>
        <td>{string($i/Nominal)}</td>
        <td>{string($i/Name)}</td>
        <td>{string($i/Value)}</td>
      </tr>
    )
    }
    </tbody></table>
  </body>
</html>