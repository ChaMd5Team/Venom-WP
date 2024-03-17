# writeup

$\varphi = o\cdot r_1 \cdot r_2 = (p-1)\cdot (q-1) = n+1 - (p+q)$

于是构造格子
$$
M =
\begin{bmatrix} 2^{144}& -o\newline 0 &n+1
\end{bmatrix}
$$
规约一下即可得到 $p+q$

然后就能分解 $n$，RSA 解密即可。