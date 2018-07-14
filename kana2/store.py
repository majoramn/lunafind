"""PostStore class"""

from . import info, post

POST_USABLE_FUNCTIONS = [
    "get_all", "get_extra", "get_media", "get_artcom", "get_notes",
    "set_paths", "write", "load",
    "verify_media", "verify_media_by_md5", "verify_media_by_filesize"
]


class PostStore(dict):
    def __init__(self, *values, store_dict=None, init_get=False):
        if store_dict:
            super().__init__(store_dict)
            return

        for value in values:
            if isinstance(value, post.Post):
                self[value.id] = value
                continue

            for post_info in info.from_auto(value):
                self[post_info["id"]] = post.Post(post_info, init_get=False)

        if init_get:
            self.map("get_all")

    # PostStore merges:

    def __add__(self, to_add):  # +
        store = to_add if isinstance(to_add, PostStore) else PostStore(to_add)
        new   = self.copy()
        new.update(store)
        return new

    def __iadd__(self, to_add):  # +=
        self = self + to_add
        return self

    def merge(self, *to_merge):
        for value in to_merge:
            store = value if isinstance(value, PostStore) else PostStore(value)
            self.update(store)

    # PostStore items removals:

    def __sub__(self, to_sub):  # -
        store = to_sub if isinstance(to_sub, PostStore) else PostStore(to_sub)
        new   = self.copy()
        for key in store:
            new.pop(key, None)
        return new

    def __isub__(self, to_sub):  # -=
        self = self - to_sub
        return self

    def subtract(self, *to_sub):
        for value in to_sub:
            store = value if isinstance(value, PostStore) else PostStore(value)
            for key in store:
                self.pop(key, None)

    # Adding single Post objects:

    def __setitem__(self, key, to_set):  # PostStore[new] = val
        to_set = to_set if isinstance(to_set, post.Post) else post.Post(to_set)
        self.update({key: to_set})

    def setdefault(self, key, default_post=None):
        if not default_post:
            return self.get(key)

        if key not in self.keys():
            self[key] = post.Post(default_post)

        return self[key]

    # Display:

    def __repr__(self):
        return "PostStore(%r)" % {k: p for k, p in self.items()}

    def __str__(self):
        return str({k: p for k, p in self.items()})

    # Comparisons:

    def __eq__(self, other_store):
        if len(self.keys()) != len(other_store.keys()):
            return False

        for key, post_ in self.items():
            if post_ != other_store.get(key):
                return False

        return True

    # Others:

    def copy(self):
        """Override dict append to return a PostStore()."""
        return PostStore(store_dict={k: p for k, p in self.items()})

    def map(self, method, *args, **kwargs):
        for post_obj in self.values():
            getattr(post_obj, method)(*args, **kwargs)


# Hack to make functions that operate on all posts,
# e.g. PostStore.get_all() calls Post.get_all on all Post objects.
for function in POST_USABLE_FUNCTIONS:
    # pylint: disable=w0122
    exec(f"def {function}(self, *args, **kwargs):\n"
         f"    self.map('{function}', *args, **kwargs)\n"
         f"PostStore.{function} = {function}", globals())
