from __future__ import annotations

from app import store
from app.passwords import check_password, hash_password


# ─── Users ────────────────────────────────────────────────────────────────────

class UserM:
    @staticmethod
    def get_all() -> list:
        return store.get_all('users')

    @staticmethod
    def needs_setup() -> bool:
        return len(store.get_all('users')) == 0

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('users', id_)

    @staticmethod
    def get_all_active() -> list:
        return [u for u in store.get_all('users') if u.get('status') == 1]

    @staticmethod
    def check_username(username: str, exclude_id=None) -> dict | None:
        try:
            exclude_int = int(exclude_id) if exclude_id is not None else None
        except (ValueError, TypeError):
            exclude_int = None
        for u in store.get_all('users'):
            if u['username'] == username:
                if exclude_int is None or u['id'] != exclude_int:
                    return u
        return None

    @staticmethod
    def login_check(username: str, password: str) -> dict | None:
        for u in store.get_all('users'):
            if u['username'] == username and u.get('status') == 1:
                if check_password(u['password'], password):
                    return u
        return None

    @staticmethod
    def create(username: str, password: str, role: int, status: int) -> int:
        return store.create('users', {
            'username': username,
            'password': hash_password(password),
            'role': int(role),
            'status': int(status),
        })

    @staticmethod
    def update(id_, username: str, role: int, status: int, password: str = None):
        data = {
            'username': username,
            'role': int(role),
            'status': int(status),
        }
        if password:
            data['password'] = hash_password(password)
        store.update('users', id_, data)

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('users', id_)


# ─── Server Roles ─────────────────────────────────────────────────────────────

class ServerRoleM:
    @staticmethod
    def get_all() -> list:
        return store.get_all('server_roles')

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('server_roles', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for r in store.get_all('server_roles'):
            if r.get('name', '').strip().lower() == key:
                return r
        return None

    @staticmethod
    def create(name: str, color: str, description: str) -> int:
        return store.create('server_roles', {
            'name': name,
            'color': color.lstrip('#'),
            'description': description,
        })

    @staticmethod
    def update(id_, name: str, color: str, description: str):
        store.update('server_roles', id_, {
            'name': name,
            'color': color.lstrip('#'),
            'description': description,
        })

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('server_roles', id_)

    @staticmethod
    def get_by_ids(ids: list) -> list:
        id_set = {int(i) for i in ids}
        return [r for r in store.get_all('server_roles') if r['id'] in id_set]


# ─── Server Locations ─────────────────────────────────────────────────────────

class ServerLocationM:
    @staticmethod
    def get_all(filters: dict = None) -> list:
        items = store.get_all('server_locations')
        if not filters:
            return items
        q = (filters.get('q') or '').lower()
        return [loc for loc in items if not q or q in loc.get('name', '').lower()]

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('server_locations', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for loc in store.get_all('server_locations'):
            if loc.get('name', '').strip().lower() == key:
                return loc
        return None

    @staticmethod
    def create(name: str, comments: str) -> int:
        return store.create('server_locations', {'name': name, 'comments': comments})

    @staticmethod
    def update(id_, name: str, comments: str):
        store.update('server_locations', id_, {'name': name, 'comments': comments})

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('server_locations', id_)

    @staticmethod
    def get_by_ids(ids: list) -> list:
        id_set = {int(i) for i in ids if i is not None}
        return [loc for loc in store.get_all('server_locations') if loc['id'] in id_set]


# ─── Products ─────────────────────────────────────────────────────────────────

class ProductM:
    @staticmethod
    def get_all(filters: dict = None) -> list:
        items = store.get_all('products')
        if not filters:
            return items
        q = (filters.get('q') or '').lower()
        return [p for p in items if not q or q in p.get('name', '').lower()]

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('products', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for p in store.get_all('products'):
            if p.get('name', '').strip().lower() == key:
                return p
        return None

    @staticmethod
    def create(name: str, comments: str) -> int:
        return store.create('products', {'name': name, 'comments': comments})

    @staticmethod
    def update(id_, name: str, comments: str):
        store.update('products', id_, {'name': name, 'comments': comments})

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('products', id_)

    @staticmethod
    def get_by_ids(ids: list) -> list:
        id_set = {int(i) for i in ids}
        return [p for p in store.get_all('products') if p['id'] in id_set]


# ─── Tags ─────────────────────────────────────────────────────────────────────

class TagM:
    @staticmethod
    def get_all(filters: dict = None) -> list:
        items = store.get_all('tags')
        if not filters:
            return items
        q = (filters.get('q') or '').lower()
        return [t for t in items if not q or q in t.get('name', '').lower()]

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('tags', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for t in store.get_all('tags'):
            if t.get('name', '').strip().lower() == key:
                return t
        return None

    @staticmethod
    def create(name: str, color: str, comments: str) -> int:
        return store.create('tags', {
            'name': name,
            'color': color.lstrip('#'),
            'comments': comments,
        })

    @staticmethod
    def update(id_, name: str, color: str, comments: str):
        store.update('tags', id_, {
            'name': name,
            'color': color.lstrip('#'),
            'comments': comments,
        })

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('tags', id_)

    @staticmethod
    def get_by_ids(ids: list) -> list:
        id_set = {int(i) for i in ids}
        return [t for t in store.get_all('tags') if t['id'] in id_set]


# ─── Programs ─────────────────────────────────────────────────────────────────

class ProgramM:
    @staticmethod
    def get_all(filters: dict = None) -> list:
        items = store.get_all('programs')
        if not filters:
            return items
        q = (filters.get('q') or '').lower()
        return [p for p in items if not q or q in p.get('name', '').lower()]

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('programs', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for p in store.get_all('programs'):
            if p.get('name', '').strip().lower() == key:
                return p
        return None

    @staticmethod
    def create(name: str, comments: str) -> int:
        return store.create('programs', {'name': name, 'comments': comments})

    @staticmethod
    def update(id_, name: str, comments: str):
        store.update('programs', id_, {'name': name, 'comments': comments})

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('programs', id_)

    @staticmethod
    def get_by_ids(ids: list) -> list:
        id_set = {int(i) for i in ids}
        return [p for p in store.get_all('programs') if p['id'] in id_set]


# ─── Servers ──────────────────────────────────────────────────────────────────

class ServerM:
    @staticmethod
    def get_distinct_os_values() -> list:
        return store.get_distinct_os_values()

    @staticmethod
    def get_all(filters: dict = None) -> list:
        servers = store.get_all('servers')
        if not filters:
            return servers

        result = []
        q = (filters.get('q') or '').lower()
        status_f = filters.get('status') or ''
        role_f = filters.get('role_id')
        product_fs = filters.get('product_ids') or []
        if not isinstance(product_fs, list):
            product_fs = [product_fs]
        product_fs = {int(p) for p in product_fs}
        program_f = filters.get('program_id')
        tag_f = filters.get('tag_id')

        for s in servers:
            if q:
                haystack = ' '.join([
                    s.get('name', ''),
                    s.get('ip_address', ''),
                    s.get('os', ''),
                    s.get('comments', ''),
                ]).lower()
                if q not in haystack:
                    continue
            if status_f and s.get('status') != status_f:
                continue
            if role_f:
                if int(role_f) not in [int(r) for r in s.get('role_ids', [])]:
                    continue
            if product_fs:
                server_products = {int(p) for p in s.get('product_ids', [])}
                if not product_fs.intersection(server_products):
                    continue
            if program_f:
                if int(program_f) not in [int(p) for p in s.get('program_ids', [])]:
                    continue
            if tag_f:
                if int(tag_f) not in [int(t) for t in s.get('tag_ids', [])]:
                    continue
            result.append(s)

        return result

    @staticmethod
    def get_one(id_) -> dict | None:
        return store.get_one('servers', id_)

    @staticmethod
    def find_by_name(name: str) -> dict | None:
        key = name.strip().lower()
        for s in store.get_all('servers'):
            if s.get('name', '').strip().lower() == key:
                return s
        return None

    @staticmethod
    def link_program(server_id: int, program_id: int) -> bool:
        """Add program_id to server if not already linked. Returns True if a new link was added."""
        server = store.get_one('servers', server_id)
        if not server:
            return False
        program_ids = [int(p) for p in server.get('program_ids', [])]
        pid = int(program_id)
        if pid in program_ids:
            return False
        program_ids.append(pid)
        ServerM.update(
            id_=server_id,
            name=server['name'],
            role_ids=server.get('role_ids', []),
            ip_address=server.get('ip_address', ''),
            url=server.get('url', ''),
            os_=server.get('os', ''),
            cpu=server.get('cpu', ''),
            cpu_cores=server.get('cpu_cores', ''),
            ram=server.get('ram', ''),
            disk=server.get('disk', ''),
            location_id=server.get('location_id'),
            comments=server.get('comments', ''),
            status=server.get('status', 'active'),
            product_ids=server.get('product_ids', []),
            program_ids=program_ids,
            tag_ids=server.get('tag_ids', []),
        )
        return True

    @staticmethod
    def link_product(server_id: int, product_id: int) -> bool:
        """Add product_id to server if not already linked. Returns True if a new link was added."""
        server = store.get_one('servers', server_id)
        if not server:
            return False
        product_ids = [int(p) for p in server.get('product_ids', [])]
        pid = int(product_id)
        if pid in product_ids:
            return False
        product_ids.append(pid)
        ServerM.update(
            id_=server_id,
            name=server['name'],
            role_ids=server.get('role_ids', []),
            ip_address=server.get('ip_address', ''),
            url=server.get('url', ''),
            os_=server.get('os', ''),
            cpu=server.get('cpu', ''),
            cpu_cores=server.get('cpu_cores', ''),
            ram=server.get('ram', ''),
            disk=server.get('disk', ''),
            location_id=server.get('location_id'),
            comments=server.get('comments', ''),
            status=server.get('status', 'active'),
            product_ids=product_ids,
            program_ids=server.get('program_ids', []),
            tag_ids=server.get('tag_ids', []),
        )
        return True

    @staticmethod
    def create(name, role_ids, ip_address, url, os_, comments, status,
               product_ids, program_ids, tag_ids,
               cpu='', cpu_cores='', ram='', disk='', location_id=None) -> int:
        return store.create('servers', {
            'name': name,
            'role_ids': [int(r) for r in role_ids],
            'ip_address': ip_address,
            'url': url,
            'os': os_,
            'cpu': cpu,
            'cpu_cores': cpu_cores,
            'ram': ram,
            'disk': disk,
            'location_id': int(location_id) if location_id else None,
            'comments': comments,
            'status': status,
            'product_ids': [int(p) for p in product_ids],
            'program_ids': [int(p) for p in program_ids],
            'tag_ids': [int(t) for t in tag_ids],
        })

    @staticmethod
    def update(id_, name, role_ids, ip_address, url, os_, comments, status,
               product_ids, program_ids, tag_ids,
               cpu='', cpu_cores='', ram='', disk='', location_id=None):
        store.update('servers', id_, {
            'name': name,
            'role_ids': [int(r) for r in role_ids],
            'ip_address': ip_address,
            'url': url,
            'os': os_,
            'cpu': cpu,
            'cpu_cores': cpu_cores,
            'ram': ram,
            'disk': disk,
            'location_id': int(location_id) if location_id else None,
            'comments': comments,
            'status': status,
            'product_ids': [int(p) for p in product_ids],
            'program_ids': [int(p) for p in program_ids],
            'tag_ids': [int(t) for t in tag_ids],
        })

    @staticmethod
    def delete(id_) -> bool:
        return store.delete('servers', id_)
