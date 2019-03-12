from spiders.NhcPublic import NhcPublic
from spiders.NhcSt import NhcSt
from spiders.Beijing import Beijing

Spiders = {
    "NhcSt": NhcSt(),
    "NhcPublic": NhcPublic(),
    "Beijing": Beijing(),
}
