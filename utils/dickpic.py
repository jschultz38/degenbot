from google_images_search import GoogleImagesSearch

import credentials

gis = GoogleImagesSearch(credentials.google_key, "23baa6b8ec2064d4a")

# define search params
# option for commonly used search param are shown below for easy reference.
# For param marked with '##':
#   - Multiselect is currently not feasible. Choose ONE option only
#   - This param can also be omitted from _search_params if you do not wish to define any value
_search_params = {
    'q': 'dick',
    'num': 10,
    'fileType': 'jpg|gif|png',
    'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
    'safe': 'active',  ##
    'imgType': 'photo'
}

# this will only search for images:
gis.search(search_params=_search_params)


for image in gis.results():
    print(image.url)




'''<script async src="https://cse.google.com/cse.js?cx=23baa6b8ec2064d4a">
</script>
<div class="gcse-search"></div>'''