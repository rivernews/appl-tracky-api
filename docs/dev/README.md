# Development Notes, Diary & Latest Roadmap

Database schema design - text format. Using this [schema design web app](https://app.quickdatabasediagrams.com/#/d/oo35Ob).

```
CustomUser
-
uuid uuid4

# both for web scrapper rating & user input
Company
-
uuid uuid4
user ManyToOne FK >- CustomUser.uuid
labels ManyToMany FK >- Label.uuid
name string
hq_location OneToOne FK >- Address.uuid
home_page OneToOne FK >- Link.uuid
ratings computed
applications computed

CompanyRating
-
uuid uuid4
source OneToOne FK >- Link.uuid
value float
company FK >- Company.uuid


Application
-
uuid uuid4
user ManyToOne FK >- CustomUser.uuid
user_company ManyToOne FK >- Company.uuid
lastest_status computed
statuses computed
position_title string
position_locations computed
job_description_page OneToOne FK >- Link.uuid
labels ManyToMany FK >- Label.uuid
source OneToOne FK >- Link.uuid

PositionLocation
-
uuid
application ManyToOne FK >- Application.uuid
location OneToOne FK >- Address.uuid


Label
-
uuid uuid4
user FK >- CustomUser.uuid
text string
color string
order int

# should we use fixed number? Or user define?
ApplicationStatus
-
uuid uuid4
text string
application ManyToOne FK >- Application.uuid
order int
date date
links computed

Link
-
uuid uuid4
text string
user ManyToOne FK >- CustomUser.uuid
url string
order int

Address
-
uuid uuid4
place_name string
country string
state string
city string
street string
raw_address string
zipcode string

ApplicationStatusLink
-
uuid
link OneToOne FK >- Link.uuid
application_status ManyToOne FK >- ApplicationStatus.uuid
```

## Production server testing

- Our react is getting closer and closer to the basic functionality goal. At this point, we will launch a initial testing on production server to see if there's any potential issues. Especially the database part. Also CORS, and other security issues in mind.

- Some prerequisites to deploy
    - Have Docker running in background
    - Better use the `deploy.sh` in the root folder to do CD. And yes, you should only need to run this file and don't have to touch anything else. But if any of the server has issue, you will have to log into AWS console or run docker locally to debug.
- Some debug tips for Docker
    - Sometimes restart docker will do the trick
    - use `docker system prune --volumes` to clean up all.
    - If docker goes wrong, it's very likely that some issues are in `.env`, `.env.sh` or `deploy.sh`. Pay attention to string variable interpolation. You may found some post talking about `.dockerignore` and large files, but that's not our case. [See your own post on Github](https://github.com/docker/compose/issues/4396).

### Resolving request issues between frontend and backend

- Resolve issues for CORS, and django's allowed hosts.
- Setup a conditional params in react for detecting prod or dev env.
- Resolve [basename](https://github.com/ReactTraining/react-router/issues/4801) in frontend react router.