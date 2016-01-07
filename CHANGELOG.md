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
