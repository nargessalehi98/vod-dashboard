# VOD-dashboard api doc

#### By Narges Salehi

#### _Input V1: auth, method , data, api_version_

#### _Url: -_

#### _User: -_

#### _Pass: -_

#### _Version: -_

#### _host: https://vodadmin.iranlms.ir_

#### _general output:  status (OK, ServerError, SystemError, ClientError, InvalidAuth, InvalidAccess), data, client_error_message, system_error_message_

####      * star values are must

## Methods

### Method: loginDashboard

```commandline
Input: username*, password*
Output: auth(JWT Toekn), admin (Admin object)
status code: 200 Ok
Access: -
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method: logoutDashboard

```commandline
Input: -
Output: -
status code: 200 Ok
Access: -
```

### Method: dashboardChangePassword

```commandline
 Input: old_password*, new_password*
 Output: Ok
 Status code: 200 
 Access: -
 ```

### Method:  addAdmin

```commandline
Input: username*, password*, title*, provider_id, avatar_url, email, access_group_ids (array of id)
Output: Ok, admin (Admin object)
Status code: 200 Ok 
Access: AddAdmin
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  editAdmin

```commandline
Input: admin_id*, username, title, email, avatar_url, status (EnumAdminStatus)
access_group_ids (array of id)
Output: Ok admin (Admin object)
Status code: 200 Ok 
Access: ModifyAdmin
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  getAdmins

```commandline
Input:  page_number*, page_limit*, status (EnumAdminStatus), access_groups_ids (array of access_group_id), search_text
Output: Ok admins (array of Admin objects), total_counts
Status code: 200 Ok 
Access: ViewAdmin
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  getDashboardProfile

```commandline
Input: -
Output: admin (Admin object)
Status code: 200 Ok 
Access:-
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  editDashboardProfile

```commandline
Input:title, email, avatar_url 
Output: admin (Admin object)
Status code: 200 Ok 
Access: EditDashboardProfile
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  resetAdminPassword

```commandline
Input:admin_id*, new_password*
Output: admin (Admin object)
Status code: 200 Ok 
Access: ModifyAdmin
```

### Object: Admin

* id: BsonObjectId
* username: str
* email: str
* title: str
* avatar_url: str
* status: Literal['Active', 'Deactivate']
* access_group_ids: list
* last_access_time: datetime
* provider_id: Optional[str]

### Method:  getAccessList

```commandline
Input: -
Output: accesses (array of Access objects) 
Status code: 200 Ok 
Access: ViewAccessGroup
```

### Object: Access

* id: BsonObjectId
* access: Literal['AddAdmin', 'ModifyAdmin', ' ViewAdmin', 'EditDashboardProfile', 'ViewAccessGroup','AddAccessGroup']

### Method:  getAccessGroups

```commandline
Input: page_number*, page_limit*, search_text
Output: access_groups (array of AccessGroup objects), total_counts
Status code: 200 Ok 
Access: ViewAccessGroup
```

### Object: AccessGroup

* id: BsonObjectId
* title: str
* accesses: list

### Method:  editAccessGroup

```commandline
Input: access_group_id*, title, accesses
Output: access_group (AccessGroup object)
Status code: 200 Ok 
Access: ModifyAccessGroup
```

### Object: AccessGroup

* id: BsonObjectId
* title: str
* accesses: list

### Method:  addAccessGroup

```commandline
Input: title*, accesses* (array of EnumAccess) 
Output: access_group (AccessGroup object)
Status code: 200 Ok 
Access: AddAccessGroup
```

### Object: AccessGroup

* id: BsonObjectId
* title: str
* accesses: list

### Method:  addProvider

```commandline
Input: name*, logo_file_id
Output: provider (Provider object) 
Status code: 200 Ok 
Access: AddProvider
```

### Object: Provider

* id: BsonObjectId 
* name: str
* dc_id: str 
* logo_file_id: str 
* url: str 

### Method:  editProvider

```commandline
Input:  provider_id*, name, logo_file_id
Output: provider ( Provider object) 
Status code: 200 Ok 
Access: ModifyProvider
```

### Object: Provider

* id: BsonObjectId 
* name: str
* dc_id: str 
* logo_file_id: str 
* url: str 

### Method:  getProviders

```commandline
Input:  page_number*, page_limit*, search_text
Output: providers (array of Provider object), total_counts
Status code: 200 Ok 
Access: ModifyProvider
```

### Object: Provider

* id: BsonObjectId
* logo_url: str
* name: list

### Method:  deleteProvider

```commandline
Input: id* (provider id)
Output: OK
Status code: 200 Ok 
Access: ViewProvider
```

### Method:  addSeries

```commandline
Input: Series object
Output: OK
Status code: 200 Ok 
Access: - 
```
### Object: Series
* title: str
* summery: str
* language: Literal['Persian', 'English']
* genre: List[str]
* age: Literal['Adults', 'Children', 'Both']
* director_id: str
* producer_id: str
* actors_id: list
* IMDB_link: Optional[str]
* tags: List[str]
* admin_id: str
* provider_id: Optional[str]


### Method:  uploadPicture

```commandline
Input: Picture data*
Output: OK
Status code: 200 Ok 
Access: - 
```
### data: Picture
* source_id: str
* type: Literal['Avatar']
* extension: Literal['JPEG', 'JPG', 'PNG']
* size: int
* name: str

### Method:  uploadContent

```commandline
Input: Content data*
Output: OK
Status code: 200 Ok 
Access: - 
```
### data: Content
#### series only
* series_id: Optional[str]
* season: Optional[int]
* episode: Optional[int]
#### movies only
* actors_id: Optional[list]
#### both
* title: str
* summery: str
* language: Optional[str]
* genre: Optional[List[str]]
* age: Optional[Literal['Adults', 'Children', 'Both']]
* director_id: Optional[str]
* producer_id: Optional[str]
* persons_id: Optional[List[str]]
* IMDB_link: Optional[str]
* tags: Optional[List[str]]
* publish_datetime: Optional[datetime] = datetime_now()
* admin_id: str
* provider_id: Optional[str]
* type: Literal['Movie', 'SeriesEpisode']

### Method:  uploadPicture

```commandline
Input: Picture data*
Output: OK
Status code: 200 Ok 
Access: - 
```
### data: Picture
* source_id: str
* type: Literal['Avatar']
* extension: Literal['JPEG', 'JPG', 'PNG']
* size: int
* name: str