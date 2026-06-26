-- SQLite to PostgreSQL Export

BEGIN TRANSACTION;

-- Table: django_migrations
CREATE TABLE "django_migrations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app" varchar(255) NOT NULL, "name" varchar(255) NOT NULL, "applied" datetime NOT NULL);

INSERT INTO django_migrations (id,app,name,applied) VALUES (1,'contenttypes','0001_initial','2026-06-16 09:05:06.071373');
INSERT INTO django_migrations (id,app,name,applied) VALUES (2,'contenttypes','0002_remove_content_type_name','2026-06-16 09:05:06.081537');
INSERT INTO django_migrations (id,app,name,applied) VALUES (3,'auth','0001_initial','2026-06-16 09:05:06.098218');
INSERT INTO django_migrations (id,app,name,applied) VALUES (4,'auth','0002_alter_permission_name_max_length','2026-06-16 09:05:06.106757');
INSERT INTO django_migrations (id,app,name,applied) VALUES (5,'auth','0003_alter_user_email_max_length','2026-06-16 09:05:06.114894');
INSERT INTO django_migrations (id,app,name,applied) VALUES (6,'auth','0004_alter_user_username_opts','2026-06-16 09:05:06.125281');
INSERT INTO django_migrations (id,app,name,applied) VALUES (7,'auth','0005_alter_user_last_login_null','2026-06-16 09:05:06.134324');
INSERT INTO django_migrations (id,app,name,applied) VALUES (8,'auth','0006_require_contenttypes_0002','2026-06-16 09:05:06.139711');
INSERT INTO django_migrations (id,app,name,applied) VALUES (9,'auth','0007_alter_validators_add_error_messages','2026-06-16 09:05:06.148117');
INSERT INTO django_migrations (id,app,name,applied) VALUES (10,'auth','0008_alter_user_username_max_length','2026-06-16 09:05:06.156469');
INSERT INTO django_migrations (id,app,name,applied) VALUES (11,'auth','0009_alter_user_last_name_max_length','2026-06-16 09:05:06.164739');
INSERT INTO django_migrations (id,app,name,applied) VALUES (12,'auth','0010_alter_group_name_max_length','2026-06-16 09:05:06.177443');
INSERT INTO django_migrations (id,app,name,applied) VALUES (13,'auth','0011_update_proxy_permissions','2026-06-16 09:05:06.181421');
INSERT INTO django_migrations (id,app,name,applied) VALUES (14,'auth','0012_alter_user_first_name_max_length','2026-06-16 09:05:06.195871');
INSERT INTO django_migrations (id,app,name,applied) VALUES (15,'core','0001_initial','2026-06-16 09:05:07.607255');
INSERT INTO django_migrations (id,app,name,applied) VALUES (16,'admin','0001_initial','2026-06-16 09:05:07.648513');
INSERT INTO django_migrations (id,app,name,applied) VALUES (17,'admin','0002_logentry_remove_auto_add','2026-06-16 09:05:07.848609');
INSERT INTO django_migrations (id,app,name,applied) VALUES (18,'admin','0003_logentry_add_action_flag_choices','2026-06-16 09:05:07.897101');
INSERT INTO django_migrations (id,app,name,applied) VALUES (19,'sessions','0001_initial','2026-06-16 09:05:07.918802');

-- Table: django_content_type
CREATE TABLE "django_content_type" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "app_label" varchar(100) NOT NULL, "model" varchar(100) NOT NULL);

INSERT INTO django_content_type (id,app_label,model) VALUES (1,'admin','logentry');
INSERT INTO django_content_type (id,app_label,model) VALUES (2,'auth','permission');
INSERT INTO django_content_type (id,app_label,model) VALUES (3,'auth','group');
INSERT INTO django_content_type (id,app_label,model) VALUES (4,'contenttypes','contenttype');
INSERT INTO django_content_type (id,app_label,model) VALUES (5,'sessions','session');
INSERT INTO django_content_type (id,app_label,model) VALUES (6,'core','user');
INSERT INTO django_content_type (id,app_label,model) VALUES (7,'core','badge');
INSERT INTO django_content_type (id,app_label,model) VALUES (8,'core','course');
INSERT INTO django_content_type (id,app_label,model) VALUES (9,'core','documentcategory');
INSERT INTO django_content_type (id,app_label,model) VALUES (10,'core','learningmodule');
INSERT INTO django_content_type (id,app_label,model) VALUES (11,'core','lesson');
INSERT INTO django_content_type (id,app_label,model) VALUES (12,'core','lessonmodule');
INSERT INTO django_content_type (id,app_label,model) VALUES (13,'core','observationchecklistitem');
INSERT INTO django_content_type (id,app_label,model) VALUES (14,'core','quiz');
INSERT INTO django_content_type (id,app_label,model) VALUES (15,'core','summativeassessment');
INSERT INTO django_content_type (id,app_label,model) VALUES (16,'core','tendersource');
INSERT INTO django_content_type (id,app_label,model) VALUES (17,'core','userbadge');
INSERT INTO django_content_type (id,app_label,model) VALUES (18,'core','tenderopportunity');
INSERT INTO django_content_type (id,app_label,model) VALUES (19,'core','task');
INSERT INTO django_content_type (id,app_label,model) VALUES (20,'core','staffannouncement');
INSERT INTO django_content_type (id,app_label,model) VALUES (21,'core','shareddocument');
INSERT INTO django_content_type (id,app_label,model) VALUES (22,'core','quizquestion');
INSERT INTO django_content_type (id,app_label,model) VALUES (23,'core','opportunity');
INSERT INTO django_content_type (id,app_label,model) VALUES (24,'core','notification');
INSERT INTO django_content_type (id,app_label,model) VALUES (25,'core','moduleevidence');
INSERT INTO django_content_type (id,app_label,model) VALUES (26,'core','meeting');
INSERT INTO django_content_type (id,app_label,model) VALUES (27,'core','logbookentry');
INSERT INTO django_content_type (id,app_label,model) VALUES (28,'core','learnerprofile');
INSERT INTO django_content_type (id,app_label,model) VALUES (29,'core','learnerdocument');
INSERT INTO django_content_type (id,app_label,model) VALUES (30,'core','forumtopic');
INSERT INTO django_content_type (id,app_label,model) VALUES (31,'core','forumpost');
INSERT INTO django_content_type (id,app_label,model) VALUES (32,'core','documentdownloadlog');
INSERT INTO django_content_type (id,app_label,model) VALUES (33,'core','dailystreak');
INSERT INTO django_content_type (id,app_label,model) VALUES (34,'core','crawllog');
INSERT INTO django_content_type (id,app_label,model) VALUES (35,'core','coursegroup');
INSERT INTO django_content_type (id,app_label,model) VALUES (36,'core','backuplog');
INSERT INTO django_content_type (id,app_label,model) VALUES (37,'core','auditlog');
INSERT INTO django_content_type (id,app_label,model) VALUES (38,'core','assignment');
INSERT INTO django_content_type (id,app_label,model) VALUES (39,'core','application');
INSERT INTO django_content_type (id,app_label,model) VALUES (40,'core','announcement');
INSERT INTO django_content_type (id,app_label,model) VALUES (41,'core','usermoduleprogress');
INSERT INTO django_content_type (id,app_label,model) VALUES (42,'core','summativeassessmentsubmission');
INSERT INTO django_content_type (id,app_label,model) VALUES (43,'core','submission');
INSERT INTO django_content_type (id,app_label,model) VALUES (44,'core','studentchecklistresult');
INSERT INTO django_content_type (id,app_label,model) VALUES (45,'core','quizattempt');
INSERT INTO django_content_type (id,app_label,model) VALUES (46,'core','progress');
INSERT INTO django_content_type (id,app_label,model) VALUES (47,'core','portfolioofevidence');
INSERT INTO django_content_type (id,app_label,model) VALUES (48,'core','lessoninteraction');
INSERT INTO django_content_type (id,app_label,model) VALUES (49,'core','certificate');
INSERT INTO django_content_type (id,app_label,model) VALUES (50,'core','attendance');
INSERT INTO django_content_type (id,app_label,model) VALUES (51,'core','assessorsignoff');

-- Table: auth_group_permissions
CREATE TABLE "auth_group_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: auth_permission
CREATE TABLE "auth_permission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "codename" varchar(100) NOT NULL, "name" varchar(255) NOT NULL);

INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (1,1,'add_logentry','Can add log entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (2,1,'change_logentry','Can change log entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (3,1,'delete_logentry','Can delete log entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (4,1,'view_logentry','Can view log entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (5,2,'add_permission','Can add permission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (6,2,'change_permission','Can change permission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (7,2,'delete_permission','Can delete permission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (8,2,'view_permission','Can view permission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (9,3,'add_group','Can add group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (10,3,'change_group','Can change group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (11,3,'delete_group','Can delete group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (12,3,'view_group','Can view group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (13,4,'add_contenttype','Can add content type');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (14,4,'change_contenttype','Can change content type');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (15,4,'delete_contenttype','Can delete content type');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (16,4,'view_contenttype','Can view content type');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (17,5,'add_session','Can add session');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (18,5,'change_session','Can change session');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (19,5,'delete_session','Can delete session');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (20,5,'view_session','Can view session');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (21,6,'add_user','Can add user');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (22,6,'change_user','Can change user');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (23,6,'delete_user','Can delete user');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (24,6,'view_user','Can view user');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (25,7,'add_badge','Can add badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (26,7,'change_badge','Can change badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (27,7,'delete_badge','Can delete badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (28,7,'view_badge','Can view badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (29,8,'add_course','Can add course');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (30,8,'change_course','Can change course');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (31,8,'delete_course','Can delete course');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (32,8,'view_course','Can view course');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (33,9,'add_documentcategory','Can add document category');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (34,9,'change_documentcategory','Can change document category');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (35,9,'delete_documentcategory','Can delete document category');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (36,9,'view_documentcategory','Can view document category');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (37,10,'add_learningmodule','Can add learning module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (38,10,'change_learningmodule','Can change learning module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (39,10,'delete_learningmodule','Can delete learning module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (40,10,'view_learningmodule','Can view learning module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (41,11,'add_lesson','Can add lesson');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (42,11,'change_lesson','Can change lesson');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (43,11,'delete_lesson','Can delete lesson');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (44,11,'view_lesson','Can view lesson');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (45,12,'add_lessonmodule','Can add lesson module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (46,12,'change_lessonmodule','Can change lesson module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (47,12,'delete_lessonmodule','Can delete lesson module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (48,12,'view_lessonmodule','Can view lesson module');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (49,13,'add_observationchecklistitem','Can add observation checklist item');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (50,13,'change_observationchecklistitem','Can change observation checklist item');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (51,13,'delete_observationchecklistitem','Can delete observation checklist item');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (52,13,'view_observationchecklistitem','Can view observation checklist item');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (53,14,'add_quiz','Can add quiz');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (54,14,'change_quiz','Can change quiz');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (55,14,'delete_quiz','Can delete quiz');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (56,14,'view_quiz','Can view quiz');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (57,15,'add_summativeassessment','Can add summative assessment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (58,15,'change_summativeassessment','Can change summative assessment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (59,15,'delete_summativeassessment','Can delete summative assessment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (60,15,'view_summativeassessment','Can view summative assessment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (61,16,'add_tendersource','Can add tender source');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (62,16,'change_tendersource','Can change tender source');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (63,16,'delete_tendersource','Can delete tender source');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (64,16,'view_tendersource','Can view tender source');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (65,17,'add_userbadge','Can add user badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (66,17,'change_userbadge','Can change user badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (67,17,'delete_userbadge','Can delete user badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (68,17,'view_userbadge','Can view user badge');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (69,18,'add_tenderopportunity','Can add tender opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (70,18,'change_tenderopportunity','Can change tender opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (71,18,'delete_tenderopportunity','Can delete tender opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (72,18,'view_tenderopportunity','Can view tender opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (73,19,'add_task','Can add task');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (74,19,'change_task','Can change task');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (75,19,'delete_task','Can delete task');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (76,19,'view_task','Can view task');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (77,20,'add_staffannouncement','Can add staff announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (78,20,'change_staffannouncement','Can change staff announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (79,20,'delete_staffannouncement','Can delete staff announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (80,20,'view_staffannouncement','Can view staff announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (81,21,'add_shareddocument','Can add shared document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (82,21,'change_shareddocument','Can change shared document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (83,21,'delete_shareddocument','Can delete shared document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (84,21,'view_shareddocument','Can view shared document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (85,22,'add_quizquestion','Can add quiz question');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (86,22,'change_quizquestion','Can change quiz question');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (87,22,'delete_quizquestion','Can delete quiz question');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (88,22,'view_quizquestion','Can view quiz question');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (89,23,'add_opportunity','Can add opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (90,23,'change_opportunity','Can change opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (91,23,'delete_opportunity','Can delete opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (92,23,'view_opportunity','Can view opportunity');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (93,24,'add_notification','Can add notification');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (94,24,'change_notification','Can change notification');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (95,24,'delete_notification','Can delete notification');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (96,24,'view_notification','Can view notification');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (97,25,'add_moduleevidence','Can add module evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (98,25,'change_moduleevidence','Can change module evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (99,25,'delete_moduleevidence','Can delete module evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (100,25,'view_moduleevidence','Can view module evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (101,26,'add_meeting','Can add meeting');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (102,26,'change_meeting','Can change meeting');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (103,26,'delete_meeting','Can delete meeting');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (104,26,'view_meeting','Can view meeting');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (105,27,'add_logbookentry','Can add logbook entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (106,27,'change_logbookentry','Can change logbook entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (107,27,'delete_logbookentry','Can delete logbook entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (108,27,'view_logbookentry','Can view logbook entry');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (109,28,'add_learnerprofile','Can add Learner Profile');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (110,28,'change_learnerprofile','Can change Learner Profile');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (111,28,'delete_learnerprofile','Can delete Learner Profile');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (112,28,'view_learnerprofile','Can view Learner Profile');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (113,29,'add_learnerdocument','Can add learner document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (114,29,'change_learnerdocument','Can change learner document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (115,29,'delete_learnerdocument','Can delete learner document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (116,29,'view_learnerdocument','Can view learner document');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (117,30,'add_forumtopic','Can add Forum Topic');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (118,30,'change_forumtopic','Can change Forum Topic');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (119,30,'delete_forumtopic','Can delete Forum Topic');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (120,30,'view_forumtopic','Can view Forum Topic');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (121,31,'add_forumpost','Can add Forum Post');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (122,31,'change_forumpost','Can change Forum Post');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (123,31,'delete_forumpost','Can delete Forum Post');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (124,31,'view_forumpost','Can view Forum Post');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (125,32,'add_documentdownloadlog','Can add document download log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (126,32,'change_documentdownloadlog','Can change document download log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (127,32,'delete_documentdownloadlog','Can delete document download log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (128,32,'view_documentdownloadlog','Can view document download log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (129,33,'add_dailystreak','Can add daily streak');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (130,33,'change_dailystreak','Can change daily streak');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (131,33,'delete_dailystreak','Can delete daily streak');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (132,33,'view_dailystreak','Can view daily streak');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (133,34,'add_crawllog','Can add crawl log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (134,34,'change_crawllog','Can change crawl log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (135,34,'delete_crawllog','Can delete crawl log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (136,34,'view_crawllog','Can view crawl log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (137,35,'add_coursegroup','Can add course group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (138,35,'change_coursegroup','Can change course group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (139,35,'delete_coursegroup','Can delete course group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (140,35,'view_coursegroup','Can view course group');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (141,36,'add_backuplog','Can add backup log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (142,36,'change_backuplog','Can change backup log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (143,36,'delete_backuplog','Can delete backup log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (144,36,'view_backuplog','Can view backup log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (145,37,'add_auditlog','Can add audit log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (146,37,'change_auditlog','Can change audit log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (147,37,'delete_auditlog','Can delete audit log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (148,37,'view_auditlog','Can view audit log');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (149,38,'add_assignment','Can add assignment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (150,38,'change_assignment','Can change assignment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (151,38,'delete_assignment','Can delete assignment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (152,38,'view_assignment','Can view assignment');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (153,39,'add_application','Can add application');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (154,39,'change_application','Can change application');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (155,39,'delete_application','Can delete application');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (156,39,'view_application','Can view application');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (157,40,'add_announcement','Can add announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (158,40,'change_announcement','Can change announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (159,40,'delete_announcement','Can delete announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (160,40,'view_announcement','Can view announcement');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (161,41,'add_usermoduleprogress','Can add user module progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (162,41,'change_usermoduleprogress','Can change user module progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (163,41,'delete_usermoduleprogress','Can delete user module progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (164,41,'view_usermoduleprogress','Can view user module progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (165,42,'add_summativeassessmentsubmission','Can add summative assessment submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (166,42,'change_summativeassessmentsubmission','Can change summative assessment submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (167,42,'delete_summativeassessmentsubmission','Can delete summative assessment submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (168,42,'view_summativeassessmentsubmission','Can view summative assessment submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (169,43,'add_submission','Can add submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (170,43,'change_submission','Can change submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (171,43,'delete_submission','Can delete submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (172,43,'view_submission','Can view submission');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (173,44,'add_studentchecklistresult','Can add student checklist result');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (174,44,'change_studentchecklistresult','Can change student checklist result');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (175,44,'delete_studentchecklistresult','Can delete student checklist result');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (176,44,'view_studentchecklistresult','Can view student checklist result');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (177,45,'add_quizattempt','Can add quiz attempt');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (178,45,'change_quizattempt','Can change quiz attempt');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (179,45,'delete_quizattempt','Can delete quiz attempt');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (180,45,'view_quizattempt','Can view quiz attempt');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (181,46,'add_progress','Can add progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (182,46,'change_progress','Can change progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (183,46,'delete_progress','Can delete progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (184,46,'view_progress','Can view progress');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (185,47,'add_portfolioofevidence','Can add portfolio of evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (186,47,'change_portfolioofevidence','Can change portfolio of evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (187,47,'delete_portfolioofevidence','Can delete portfolio of evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (188,47,'view_portfolioofevidence','Can view portfolio of evidence');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (189,48,'add_lessoninteraction','Can add lesson interaction');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (190,48,'change_lessoninteraction','Can change lesson interaction');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (191,48,'delete_lessoninteraction','Can delete lesson interaction');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (192,48,'view_lessoninteraction','Can view lesson interaction');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (193,49,'add_certificate','Can add certificate');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (194,49,'change_certificate','Can change certificate');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (195,49,'delete_certificate','Can delete certificate');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (196,49,'view_certificate','Can view certificate');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (197,50,'add_attendance','Can add attendance');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (198,50,'change_attendance','Can change attendance');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (199,50,'delete_attendance','Can delete attendance');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (200,50,'view_attendance','Can view attendance');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (201,51,'add_assessorsignoff','Can add assessor sign off');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (202,51,'change_assessorsignoff','Can change assessor sign off');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (203,51,'delete_assessorsignoff','Can delete assessor sign off');
INSERT INTO auth_permission (id,content_type_id,codename,name) VALUES (204,51,'view_assessorsignoff','Can view assessor sign off');

-- Table: auth_group
CREATE TABLE "auth_group" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(150) NOT NULL UNIQUE);

-- Table: core_user
CREATE TABLE "core_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "role" varchar(20) NOT NULL, "email" varchar(254) NOT NULL UNIQUE, "phone" varchar(20) NULL, "profile_picture" varchar(100) NULL, "email_verified" bool NOT NULL, "verification_token" varchar(100) NULL, "reset_password_token" varchar(100) NULL, "reset_password_expires" datetime NULL, "id_number" varchar(20) NULL, "date_of_birth" date NULL, "gender" varchar(10) NULL, "nationality" varchar(100) NULL, "contact_number" varchar(20) NULL, "disability" text NULL, "preferred_language" varchar(50) NOT NULL, "is_approved" bool NOT NULL, "approved_at" datetime NULL, "department" varchar(30) NULL);

INSERT INTO core_user (id,password,last_login,is_superuser,username,first_name,last_name,is_staff,is_active,date_joined,role,email,phone,profile_picture,email_verified,verification_token,reset_password_token,reset_password_expires,id_number,date_of_birth,gender,nationality,contact_number,disability,preferred_language,is_approved,approved_at,department) VALUES (1,'pbkdf2_sha256$600000$bRyKcsVbVk6IiT9BlGl7ms$rnBnSYDbSdv6ZD1holM8J/WHSCpUY0tLoM0kSPUntQI=','2026-06-16 10:44:16.143178',1,'Nqobani','','',1,1,'2026-06-16 09:05:42.954330','student','sakhile@malitinne.co.za',NULL,'',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','English',1,NULL,NULL);
INSERT INTO core_user (id,password,last_login,is_superuser,username,first_name,last_name,is_staff,is_active,date_joined,role,email,phone,profile_picture,email_verified,verification_token,reset_password_token,reset_password_expires,id_number,date_of_birth,gender,nationality,contact_number,disability,preferred_language,is_approved,approved_at,department) VALUES (2,'pbkdf2_sha256$600000$xAI2TmWtPdEzjB0TtbNfjE$ncIrtqUBvNqNIEEp8GtT3oycObOrJ3UnKbg7DXT4gwo=','2026-06-16 15:34:47.180328',0,'admin','Mondli','Dlamini',0,1,'2026-06-16 09:35:30.738353','admin','sah.sakhile@gmail.com',NULL,'',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'0782071890','','English',1,NULL,NULL);
INSERT INTO core_user (id,password,last_login,is_superuser,username,first_name,last_name,is_staff,is_active,date_joined,role,email,phone,profile_picture,email_verified,verification_token,reset_password_token,reset_password_expires,id_number,date_of_birth,gender,nationality,contact_number,disability,preferred_language,is_approved,approved_at,department) VALUES (3,'Malitinne@2019',NULL,0,'Phumlani','Phumlani','Phakathi',0,1,'2026-06-16 09:38:59.800007','instructor','phumlani.facilitator@malitinne.co.za',NULL,'',0,NULL,NULL,NULL,NULL,NULL,'male','South African',NULL,'','English',1,NULL,NULL);
INSERT INTO core_user (id,password,last_login,is_superuser,username,first_name,last_name,is_staff,is_active,date_joined,role,email,phone,profile_picture,email_verified,verification_token,reset_password_token,reset_password_expires,id_number,date_of_birth,gender,nationality,contact_number,disability,preferred_language,is_approved,approved_at,department) VALUES (4,'pbkdf2_sha256$600000$RArVNCHww73HdXRPZpVo30$MD045Fpzw7eSB20C19ajDBpj+oHx2iBT8tIRkPRSiBY=',NULL,1,'newadmin','','',1,1,'2026-06-16 09:46:03.433681','admin','admin@malitinne.co.za',NULL,'',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'English',1,NULL,NULL);

-- Table: core_user_groups
CREATE TABLE "core_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_user_user_permissions
CREATE TABLE "core_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_badge
CREATE TABLE "core_badge" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "icon" varchar(50) NOT NULL, "points_required" integer NOT NULL, "lessons_completed" integer NOT NULL, "courses_completed" integer NOT NULL);

-- Table: core_course
CREATE TABLE "core_course" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "slug" varchar(50) NOT NULL UNIQUE, "description" text NOT NULL, "short_description" varchar(300) NOT NULL, "created_at" datetime NOT NULL, "featured_image" varchar(100) NULL, "level" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "price" decimal NOT NULL, "average_rating" real NOT NULL, "total_reviews" integer NOT NULL, "instructor_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_course_students
CREATE TABLE "core_course_students" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_documentcategory
CREATE TABLE "core_documentcategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "slug" varchar(50) NOT NULL UNIQUE, "description" text NOT NULL, "icon" varchar(50) NOT NULL, "order" integer NOT NULL, "parent_id" bigint NULL REFERENCES "core_documentcategory" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_learningmodule
CREATE TABLE "core_learningmodule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "order" integer NOT NULL, "is_visible" bool NOT NULL, "module_type" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_lesson
CREATE TABLE "core_lesson" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "content" text NOT NULL, "video_url" varchar(200) NULL, "document" varchar(100) NULL, "duration" integer NOT NULL, "order" integer NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "module_id" bigint NULL REFERENCES "core_learningmodule" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_lessonmodule
CREATE TABLE "core_lessonmodule" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "content" text NOT NULL, "content_type" varchar(20) NOT NULL, "order" integer NOT NULL, "is_locked" bool NOT NULL, "time_estimate" integer NOT NULL, "points" integer NOT NULL, "lesson_id" bigint NOT NULL REFERENCES "core_lesson" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_observationchecklistitem
CREATE TABLE "core_observationchecklistitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "description" varchar(500) NOT NULL, "order" integer NOT NULL, "module_id" bigint NOT NULL REFERENCES "core_learningmodule" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_quiz
CREATE TABLE "core_quiz" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "passing_score" integer NOT NULL, "time_limit" integer NOT NULL, "lesson_id" bigint NOT NULL UNIQUE REFERENCES "core_lesson" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_summativeassessment
CREATE TABLE "core_summativeassessment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "instructions" text NOT NULL, "due_date" datetime NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_tendersource
CREATE TABLE "core_tendersource" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "source_type" varchar(50) NOT NULL, "base_url" varchar(200) NOT NULL, "search_keywords" text NOT NULL, "is_active" bool NOT NULL, "last_crawled" datetime NULL, "crawl_frequency_hours" integer NOT NULL);

-- Table: core_userbadge
CREATE TABLE "core_userbadge" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "earned_at" datetime NOT NULL, "badge_id" bigint NOT NULL REFERENCES "core_badge" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_tenderopportunity
CREATE TABLE "core_tenderopportunity" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "tender_id" varchar(100) NOT NULL, "title" varchar(500) NOT NULL, "description" text NOT NULL, "category" varchar(50) NOT NULL, "published_date" date NULL, "closing_date" date NOT NULL, "opening_date" date NULL, "estimated_value" varchar(200) NOT NULL, "bidder_deposit" varchar(200) NOT NULL, "location" varchar(200) NOT NULL, "department" varchar(300) NOT NULL, "document_url" varchar(200) NOT NULL, "local_document" varchar(100) NULL, "ai_relevance_score" real NOT NULL, "ai_confidence" real NOT NULL, "ai_match_reasons" text NOT NULL, "internal_notes" text NOT NULL, "status" varchar(20) NOT NULL, "follow_up_date" date NULL, "follow_up_notes" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "assigned_to_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "source_id" bigint NULL REFERENCES "core_tendersource" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_task
CREATE TABLE "core_task" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "due_date" date NULL, "status" varchar(20) NOT NULL, "priority" varchar(10) NOT NULL, "created_at" datetime NOT NULL, "assigned_to_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_staffannouncement
CREATE TABLE "core_staffannouncement" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "content" text NOT NULL, "category" varchar(20) NOT NULL, "is_pinned" bool NOT NULL, "created_at" datetime NOT NULL, "author_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_shareddocument
CREATE TABLE "core_shareddocument" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(255) NOT NULL, "description" text NOT NULL, "file" varchar(100) NOT NULL, "file_name" varchar(500) NOT NULL, "file_size" bigint NOT NULL, "mime_type" varchar(100) NOT NULL, "version" varchar(20) NOT NULL, "visibility" varchar(20) NOT NULL, "uploaded_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "tags" varchar(500) NOT NULL, "download_count" integer NOT NULL, "category_id" bigint NULL REFERENCES "core_documentcategory" ("id") DEFERRABLE INITIALLY DEFERRED, "previous_version_id" bigint NULL REFERENCES "core_shareddocument" ("id") DEFERRABLE INITIALLY DEFERRED, "uploaded_by_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO core_shareddocument (id,title,description,file,file_name,file_size,mime_type,version,visibility,uploaded_at,updated_at,tags,download_count,category_id,previous_version_id,uploaded_by_id) VALUES (1,'Malitinne company profile 2024','','shared_drive/2026/06/Malitinne_company_profile_2024_9CAxSfA.pdf','Malitinne company profile 2024.pdf',1947004,'application/pdf','1.0','all_staff','2026-06-16 10:42:09.093283','2026-06-16 10:42:09.093283','',0,NULL,NULL,2);

-- Table: core_shareddocument_allowed_departments
CREATE TABLE "core_shareddocument_allowed_departments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "shareddocument_id" bigint NOT NULL REFERENCES "core_shareddocument" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_quizquestion
CREATE TABLE "core_quizquestion" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "question_text" text NOT NULL, "question_type" varchar(20) NOT NULL, "points" integer NOT NULL, "order" integer NOT NULL, "option_a" varchar(500) NOT NULL, "option_b" varchar(500) NOT NULL, "option_c" varchar(500) NOT NULL, "option_d" varchar(500) NOT NULL, "correct_answer" varchar(255) NOT NULL, "quiz_id" bigint NOT NULL REFERENCES "core_quiz" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_opportunity
CREATE TABLE "core_opportunity" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "opportunity_type" varchar(50) NOT NULL, "reference_number" varchar(50) NOT NULL UNIQUE, "description" text NOT NULL, "requirements" text NOT NULL, "responsibilities" text NOT NULL, "location" varchar(200) NOT NULL, "remote_options" bool NOT NULL, "stipend_amount" varchar(100) NOT NULL, "funding_amount" varchar(100) NOT NULL, "opening_date" date NOT NULL, "closing_date" date NOT NULL, "expected_start_date" date NULL, "available_positions" integer NOT NULL, "positions_filled" integer NOT NULL, "status" varchar(20) NOT NULL, "featured" bool NOT NULL, "priority" integer NOT NULL, "contact_email" varchar(254) NOT NULL, "contact_person" varchar(100) NOT NULL, "application_instructions" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "created_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_notification
CREATE TABLE "core_notification" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "message" text NOT NULL, "is_read" bool NOT NULL, "created_at" datetime NOT NULL, "link" varchar(500) NULL, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO core_notification (id,title,message,is_read,created_at,link,user_id) VALUES (1,'New Document: Malitinne company profile 2024','admin shared "Malitinne company profile 2024" in the document drive.',0,'2026-06-16 10:42:09.127813','/shared-drive/',2);
INSERT INTO core_notification (id,title,message,is_read,created_at,link,user_id) VALUES (2,'New Document: Malitinne company profile 2024','admin shared "Malitinne company profile 2024" in the document drive.',0,'2026-06-16 10:42:09.152635','/shared-drive/',3);
INSERT INTO core_notification (id,title,message,is_read,created_at,link,user_id) VALUES (3,'New Document: Malitinne company profile 2024','admin shared "Malitinne company profile 2024" in the document drive.',0,'2026-06-16 10:42:09.179956','/shared-drive/',4);

-- Table: core_moduleevidence
CREATE TABLE "core_moduleevidence" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "file" varchar(100) NOT NULL, "description" text NULL, "uploaded_at" datetime NOT NULL, "is_verified" bool NOT NULL, "verified_at" datetime NULL, "module_id" bigint NOT NULL REFERENCES "core_learningmodule" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "verified_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_meeting
CREATE TABLE "core_meeting" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "start_time" datetime NOT NULL, "end_time" datetime NOT NULL, "location" varchar(255) NOT NULL, "organizer_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_meeting_attendees
CREATE TABLE "core_meeting_attendees" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "meeting_id" bigint NOT NULL REFERENCES "core_meeting" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_logbookentry
CREATE TABLE "core_logbookentry" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "entry_date" date NOT NULL, "hours_spent" decimal NOT NULL, "description" text NOT NULL, "skills_learned" text NULL, "supervisor_comments" text NULL, "attachment" varchar(100) NULL, "supervisor_approved" bool NOT NULL, "approved_date" datetime NULL, "created_at" datetime NOT NULL, "approved_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "module_id" bigint NULL REFERENCES "core_learningmodule" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_learnerprofile
CREATE TABLE "core_learnerprofile" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "physical_address" text NULL, "emergency_contact_name" varchar(200) NULL, "emergency_contact_phone" varchar(20) NULL, "host_company_name" varchar(255) NULL, "mou_file" varchar(100) NULL, "mou_start_date" date NULL, "mou_end_date" date NULL, "supervisor_name" varchar(200) NULL, "supervisor_phone" varchar(20) NULL, "supervisor_email" varchar(254) NULL, "enrollment_date" date NULL, "expected_completion_date" date NULL, "assessment_notes" text NULL, "certificate_issued" bool NOT NULL, "certificate_issued_date" date NULL, "popia_consent" bool NOT NULL, "popia_consent_date" datetime NULL, "data_processing_consent" bool NOT NULL, "profile_updated" datetime NOT NULL, "current_course_id" bigint NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL UNIQUE REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO core_learnerprofile (id,physical_address,emergency_contact_name,emergency_contact_phone,host_company_name,mou_file,mou_start_date,mou_end_date,supervisor_name,supervisor_phone,supervisor_email,enrollment_date,expected_completion_date,assessment_notes,certificate_issued,certificate_issued_date,popia_consent,popia_consent_date,data_processing_consent,profile_updated,current_course_id,user_id) VALUES (1,NULL,NULL,NULL,NULL,'',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,0,NULL,0,'2026-06-16 14:18:01.038427',NULL,4);

-- Table: core_learnerdocument
CREATE TABLE "core_learnerdocument" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "document_type" varchar(50) NOT NULL, "title" varchar(200) NULL, "file" varchar(100) NOT NULL, "file_name" varchar(500) NOT NULL, "file_size" integer NOT NULL, "description" text NULL, "upload_date" datetime NOT NULL, "is_verified" bool NOT NULL, "verified_date" datetime NULL, "uploaded_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "verified_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_forumtopic
CREATE TABLE "core_forumtopic" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(300) NOT NULL, "content" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "is_ticket" bool NOT NULL, "is_resolved" bool NOT NULL, "resolved_at" datetime NULL, "priority" varchar(20) NOT NULL, "author_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "lesson_id" bigint NOT NULL REFERENCES "core_lesson" ("id") DEFERRABLE INITIALLY DEFERRED, "project_id" bigint NULL REFERENCES "core_tenderopportunity" ("id") DEFERRABLE INITIALLY DEFERRED, "resolved_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_forumpost
CREATE TABLE "core_forumpost" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "content" text NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "likes_count" integer NOT NULL, "author_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "parent_id" bigint NULL REFERENCES "core_forumpost" ("id") DEFERRABLE INITIALLY DEFERRED, "topic_id" bigint NOT NULL REFERENCES "core_forumtopic" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_documentdownloadlog
CREATE TABLE "core_documentdownloadlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "downloaded_at" datetime NOT NULL, "ip_address" char(39) NULL, "document_id" bigint NOT NULL REFERENCES "core_shareddocument" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_dailystreak
CREATE TABLE "core_dailystreak" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "current_streak" integer NOT NULL, "longest_streak" integer NOT NULL, "last_active" date NOT NULL, "total_xp" integer NOT NULL, "level" integer NOT NULL, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_crawllog
CREATE TABLE "core_crawllog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "started_at" datetime NOT NULL, "completed_at" datetime NULL, "opportunities_found" integer NOT NULL, "opportunities_new" integer NOT NULL, "status" varchar(50) NOT NULL, "error_message" text NOT NULL, "source_id" bigint NOT NULL REFERENCES "core_tendersource" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_coursegroup
CREATE TABLE "core_coursegroup" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "created_by_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_coursegroup_members
CREATE TABLE "core_coursegroup_members" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "coursegroup_id" bigint NOT NULL REFERENCES "core_coursegroup" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_backuplog
CREATE TABLE "core_backuplog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "backup_timestamp" datetime NOT NULL, "backup_type" varchar(50) NOT NULL, "backup_size" bigint NOT NULL, "status" varchar(20) NOT NULL, "notes" text NULL, "initiated_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_auditlog
CREATE TABLE "core_auditlog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "action" varchar(20) NOT NULL, "resource_type" varchar(100) NOT NULL, "resource_id" integer NULL, "ip_address" char(39) NULL, "user_agent" text NULL, "timestamp" datetime NOT NULL, "details" text NOT NULL CHECK ((JSON_VALID("details") OR "details" IS NULL)), "user_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (1,'ai_query','',NULL,'127.0.0.1',NULL,'2026-06-16 10:39:10.685011','{"query": "List inactive learners", "response_type": "inactive_learners"}',2);
INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (2,'ai_query','',NULL,'127.0.0.1',NULL,'2026-06-16 10:39:10.825124','{"query": "List inactive learners", "response_type": "inactive_learners"}',2);
INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (3,'ai_query','',NULL,'127.0.0.1',NULL,'2026-06-16 10:39:18.652069','{"query": "Give me a system summary", "response_type": "summary"}',2);
INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (4,'ai_query','',NULL,'127.0.0.1',NULL,'2026-06-16 10:39:27.741206','{"query": "Show projects with low attendance", "response_type": "help"}',2);
INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (5,'ai_query','',NULL,'127.0.0.1',NULL,'2026-06-16 10:39:32.305945','{"query": "Show open tickets", "response_type": "tickets"}',2);
INSERT INTO core_auditlog (id,action,resource_type,resource_id,ip_address,user_agent,timestamp,details,user_id) VALUES (6,'view','LearnerProfile',4,'127.0.0.1',NULL,'2026-06-16 14:18:01.059529','{}',2);

-- Table: core_assignment
CREATE TABLE "core_assignment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "description" text NOT NULL, "due_date" datetime NOT NULL, "total_points" integer NOT NULL, "created_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_application
CREATE TABLE "core_application" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "application_number" varchar(50) NOT NULL UNIQUE, "first_name" varchar(100) NOT NULL, "last_name" varchar(100) NOT NULL, "email" varchar(254) NOT NULL, "phone_number" varchar(20) NOT NULL, "alternative_phone" varchar(20) NOT NULL, "id_number" varchar(20) NOT NULL, "date_of_birth" date NOT NULL, "gender" varchar(20) NOT NULL, "race" varchar(50) NOT NULL, "disability" varchar(100) NOT NULL, "address" text NOT NULL, "city" varchar(100) NOT NULL, "province" varchar(50) NOT NULL, "postal_code" varchar(10) NOT NULL, "highest_qualification" varchar(200) NOT NULL, "institution" varchar(200) NOT NULL, "year_completed" integer NOT NULL, "field_of_study" varchar(200) NOT NULL, "work_experience" text NOT NULL, "skills" text NOT NULL, "cv" varchar(100) NULL, "cover_letter" varchar(100) NULL, "id_document" varchar(100) NULL, "qualifications" varchar(100) NULL, "hear_about_us" varchar(200) NOT NULL, "additional_info" text NOT NULL, "status" varchar(20) NOT NULL, "status_notes" text NOT NULL, "reviewed_at" datetime NULL, "score" integer NULL, "submitted_at" datetime NOT NULL, "ip_address" char(39) NULL, "user_agent" text NOT NULL, "opportunity_id" bigint NOT NULL REFERENCES "core_opportunity" ("id") DEFERRABLE INITIALLY DEFERRED, "reviewed_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_announcement
CREATE TABLE "core_announcement" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(200) NOT NULL, "content" text NOT NULL, "is_pinned" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "author_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_usermoduleprogress
CREATE TABLE "core_usermoduleprogress" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "completed" bool NOT NULL, "completed_at" datetime NULL, "time_spent" integer NOT NULL, "score" integer NULL, "attempts" integer NOT NULL, "module_id" bigint NOT NULL REFERENCES "core_lessonmodule" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_summativeassessmentsubmission
CREATE TABLE "core_summativeassessmentsubmission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file_upload" varchar(100) NOT NULL, "submitted_at" datetime NOT NULL, "result" varchar(20) NOT NULL, "assessed_at" datetime NULL, "feedback" text NULL, "assessed_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "assessment_id" bigint NOT NULL REFERENCES "core_summativeassessment" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_submission
CREATE TABLE "core_submission" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "file_upload" varchar(100) NOT NULL, "submitted_at" datetime NOT NULL, "grade" integer NULL, "feedback" text NULL, "assignment_id" bigint NOT NULL REFERENCES "core_assignment" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_studentchecklistresult
CREATE TABLE "core_studentchecklistresult" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "is_competent" bool NOT NULL, "assessed_at" datetime NULL, "comments" text NULL, "assessed_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "item_id" bigint NOT NULL REFERENCES "core_observationchecklistitem" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_quizattempt
CREATE TABLE "core_quizattempt" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "score" integer NULL, "percentage" real NULL, "passed" bool NOT NULL, "answers" text NOT NULL CHECK ((JSON_VALID("answers") OR "answers" IS NULL)), "started_at" datetime NOT NULL, "completed_at" datetime NULL, "quiz_id" bigint NOT NULL REFERENCES "core_quiz" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_progress
CREATE TABLE "core_progress" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "completed_at" datetime NULL, "certificate_issued" bool NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_progress_completed_assignments
CREATE TABLE "core_progress_completed_assignments" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "progress_id" bigint NOT NULL REFERENCES "core_progress" ("id") DEFERRABLE INITIALLY DEFERRED, "assignment_id" bigint NOT NULL REFERENCES "core_assignment" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_progress_completed_lessons
CREATE TABLE "core_progress_completed_lessons" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "progress_id" bigint NOT NULL REFERENCES "core_progress" ("id") DEFERRABLE INITIALLY DEFERRED, "lesson_id" bigint NOT NULL REFERENCES "core_lesson" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_progress_completed_quizzes
CREATE TABLE "core_progress_completed_quizzes" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "progress_id" bigint NOT NULL REFERENCES "core_progress" ("id") DEFERRABLE INITIALLY DEFERRED, "quiz_id" bigint NOT NULL REFERENCES "core_quiz" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_portfolioofevidence
CREATE TABLE "core_portfolioofevidence" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "submitted_at" datetime NULL, "reviewed_at" datetime NULL, "notes" text NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "reviewed_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_lessoninteraction
CREATE TABLE "core_lessoninteraction" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "last_activity" datetime NOT NULL, "total_time_spent" integer NOT NULL, "modules_completed" integer NOT NULL, "last_module_viewed" integer NOT NULL, "completed" bool NOT NULL, "completed_at" datetime NULL, "lesson_id" bigint NOT NULL REFERENCES "core_lesson" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_certificate
CREATE TABLE "core_certificate" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "certificate_number" varchar(100) NOT NULL UNIQUE, "issued_at" datetime NOT NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_attendance
CREATE TABLE "core_attendance" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "date" date NOT NULL, "status" varchar(20) NOT NULL, "notes" text NULL, "course_id" bigint NOT NULL REFERENCES "core_course" ("id") DEFERRABLE INITIALLY DEFERRED, "marked_by_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: core_assessorsignoff
CREATE TABLE "core_assessorsignoff" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "outcome" varchar(20) NOT NULL, "comments" text NULL, "signed_at" datetime NOT NULL, "assessor_id" bigint NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "module_id" bigint NOT NULL REFERENCES "core_learningmodule" ("id") DEFERRABLE INITIALLY DEFERRED, "student_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED);

-- Table: django_admin_log
CREATE TABLE "django_admin_log" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "object_id" text NULL, "object_repr" varchar(200) NOT NULL, "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0), "change_message" text NOT NULL, "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" bigint NOT NULL REFERENCES "core_user" ("id") DEFERRABLE INITIALLY DEFERRED, "action_time" datetime NOT NULL);

INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (1,'2','admin (admin)',1,'[{"added": {}}]',6,1,'2026-06-16 09:35:30.758089');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (2,'2','admin (admin)',2,'[{"changed": {"fields": ["Is approved"]}}]',6,1,'2026-06-16 09:35:44.081607');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (3,'1','Nqobani (student)',2,'[{"changed": {"fields": ["Is approved"]}}]',6,1,'2026-06-16 09:35:58.379270');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (4,'2','admin (admin)',2,'[]',6,1,'2026-06-16 09:37:18.178975');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (5,'3','Phumlani (admin)',1,'[{"added": {}}]',6,1,'2026-06-16 09:38:59.811177');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (6,'3','Phumlani (instructor)',2,'[{"changed": {"fields": ["Role"]}}]',6,1,'2026-06-16 09:39:23.417728');
INSERT INTO django_admin_log (id,object_id,object_repr,action_flag,change_message,content_type_id,user_id,action_time) VALUES (7,'3','Phumlani (instructor)',2,'[{"changed": {"fields": ["Password", "Gender", "Nationality"]}}]',6,1,'2026-06-16 09:45:21.228503');

-- Table: django_session
CREATE TABLE "django_session" ("session_key" varchar(40) NOT NULL PRIMARY KEY, "session_data" text NOT NULL, "expire_date" datetime NOT NULL);

INSERT INTO django_session (session_key,session_data,expire_date) VALUES ('dajxdmptljup5w6spt4ace0y17biqlx8','.eJxVjMsOwiAUBf-FtSEXECou3fsN5D5QqgaS0q6M_26bdKHbMzPnrRIuc0lLz1MaRZ2VVYffjZCfuW5AHljvTXOr8zSS3hS9066vTfLrsrt_BwV7WeuB2FlwNlo_WASSEyMd2UQDFMDfPEahkCMzgXcuABrjKTMgrxCM-nwB2Xw30A:1wZVoN:S2l_swNbNd0EMTc2VmfcwECJzVw9yNm-bBT7G9wfrhM','2026-06-30 15:34:47.189740');


COMMIT;
