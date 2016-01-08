v1.2
======

* Quicky and dirty upgrade to twx.botapi 2.0.1 to include inline stuff and file downloading. Even though it was a major upgrade to twx.botapi (they changed a few classes), I'm keeping it as a minor upgrade as there was no database impact for tgbotplug. In the future there should be a v2.0 that will have the database revisited

Impact:
* Review the code where you access twx.botapi.GroupChat directly (in case you do). There's a new parameter to distinguish chat types (Chat.type) instead of using isinstance()

v1.1
======

* Renamed tgbot.models to tgbot.database: database_proxy was a global variable and it wouldn't allow a single process to declare more than one bot with different databases - fixed by using a model_factory
* As models are now available only to TGBot instances, TGPluginBase now contains a `bot` property that is set by the bot instance itself (when it is initialized). The only downside is that one instance of a plugin can attached to a single instance of a bot, but the upside is that all plugin methods were simplified without the need of moving bot parameter around.

Impact:
* Review all the places where you access models, as now they are only available through the bot instance (not the module)
* Remove bot parameter from your plugin methods and use self.bot instead

<= v1.0.4
=======

* Untracked / initial release
