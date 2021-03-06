# thaiaddress: A Parser for Thai Address

Parser for Thai address. ไลบรารี่เพื่อแยกแยะชื่อ/ที่อยู่/รหัสไปรษณีย์/เบอร์โทรศัพท์

## Installing

```sh
git clone https://github.com/425degree-developers/thaiaddress
cd thaiaddress
pip install .
```

## Example Usage

```py
import thaiaddress
thaiaddress.parse("นายปรายุ้ด จันทร์กะเพรา 099-999-9999 25/25 ถ.พุทธมณฑล สาย 4 ต. ศาลายา อ.พุทธมณฑล จ.นครปฐม 73170")

>>> {
    'text': 'นายปรายุ้ด จันทร์กะเพรา 25/25 ถ.พุทธมณฑล สาย 4 ต. ศาลายา อ.พุทธมณฑล จ.นครปฐม 73170',
    'name': 'นายปรายุ้ด จันทร์กะเพรา',
    'address': '25/25 ถ.พุทธมณฑล สาย 4',
    'location': 'ต. ศาลายา อ.พุทธมณฑล จ.นครปฐม',
    'postal_code': '73170',
    'phone_number': '0999999999',
    'email': ''
}
```

### Display output on Jupyter notebook

<img src="images/example-usage.png" />

## Development Plan

- This is an early version of our parser with very little data. We will make a better model relatively soon.

## Developers

- [425 Degree Co., Bangkok, Thailand](https://www.425degree.com/)
