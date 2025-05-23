## 1. 项目环境管理

平时在开发项目的过程中，常常因为开发环境、测试环境、演示环境、正式环境等各种环境的存在且不同从而影响开发进度。开发系统时，项目环境管理的重要性就凸显出来了。通过下面几个实例来了解一下项目环境管理的重要性。

-  开发人员在开发环境开发好了功能接口，并在开发环境中自测无问题，直接提交到测试环境，测试人员也测试无问题，提交到了正式运行环境，但是偏偏就在正式运行环境报了错，最后排查是正式环境的JDK版本和开发、测试环境的JDK版本不一致，导致代码出错。
- 开发人员在开发环境中登录测试均无问题，但是测试人员在测试环境中无法登录，最后排查是测试环境的Nginx内部转发出了问题，因为开发环境和测试环境均不是同一个部署，所以部署方式不同，就可能会造成不同的结果。
- 一个开发完成很久的项目，突然需要给新的客户进行演示，且时间要求很紧张，但是之前的开发环境和测试环境均被收回，那么找人再一步一步安装演示环境就很浪费时间。
- 客户发现正式环境的数据有部分乱码问题，但是开发人员反复从开发环境寻找问题（因客户是隐私内网部署系统），均未找到问题所在，最后客户那边自查发现是服务器系统编码有问题，虽然客户自查出来了，但是这样的效率是很低的。

从上面几个开发过程中我真实遇到的坑不难看出，项目环境管理势在必行。
