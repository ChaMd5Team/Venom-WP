### 题目要求
本题是chrome上经典的T-Rex Runner小游戏，要求得到114514分值就可以获取flag。


### 解法一
在console里可以看到速通秘籍，直接给一个md5值，猜想是flag值的md5值，访问www.chamd5.org，注册后登录查询即可。


### 解法二
chrome的T-Rex Runner可以自动跳，以下代码网上一搜就有
```js
function TrexRunnerBot() {
  const makeKeyArgs = (keyCode) => {
    const preventDefault = () => void 0;
    return {keyCode, preventDefault};
  };
  const upKeyArgs = makeKeyArgs(38);
  const downKeyArgs = makeKeyArgs(40);
  const startArgs = makeKeyArgs(32);
  if (!Runner().playing) {
    Runner().onKeyDown(startArgs);
    setTimeout(() => {
      Runner().onKeyUp(startArgs);
    }, 500);
  }
  function conquerTheGame() {
    if (!Runner || !Runner().horizon.obstacles[0]) return;
    const obstacle = Runner().horizon.obstacles[0];
    if (obstacle.typeConfig && obstacle.typeConfig.type === 'SNACK') return;
    if (needsToTackle(obstacle) && closeEnoughToTackle(obstacle)) tackle(obstacle);
  }
  function needsToTackle(obstacle) {
    return obstacle.yPos !== 50;
  }
  function closeEnoughToTackle(obstacle) {
    return obstacle.xPos <= Runner().currentSpeed * 18;
  }
  function tackle(obstacle) {
    if (isDuckable(obstacle)) {
      duck();
    } else {
      jumpOver(obstacle);
    }
  }
  function isDuckable(obstacle) {
    return obstacle.yPos === 50;
  }
  function duck() {
    Runner().onKeyDown(downKeyArgs);
    setTimeout(() => {
      Runner().onKeyUp(downKeyArgs);
    }, 500);
  }
  function jumpOver(obstacle) {
    if (isNextObstacleCloseTo(obstacle))
      jumpFast();
    else
      Runner().onKeyDown(upKeyArgs);
  }
  function isNextObstacleCloseTo(currentObstacle) {
    const nextObstacle = Runner().horizon.obstacles[1];
 
    return nextObstacle && nextObstacle.xPos - currentObstacle.xPos <= Runner().currentSpeed * 42;
  }
  function jumpFast() {
    Runner().onKeyDown(upKeyArgs);
    Runner().onKeyUp(upKeyArgs);
  }
  return {conquerTheGame: conquerTheGame};
}
let bot = TrexRunnerBot();
let botInterval = setInterval(bot.conquerTheGame, 2);
```

但是要达到114514分需要很长时间，那只能修改js变量了。可以参考网上的一些代码，发现distanceRan就是最远距离，修改该值（要设置较大，并非设置114514就可以，要设置114514/0.25以上）

```js
Runner().distanceRan=1000000000;
```

然后再动下，就会看到弹框上的flag。


### 解法三
js/game.js是经过js中级混淆的，要是这方面有能力的话，可以直接从这入手。可以先搜索alert函数，然后从前后看起，来进行分析。


