### Useful for checking live iproxy connections
```
$ netstat -vanp tcp | grep 2222
```

Output example: 
```
markdavis@Marks-Air ~ % netstat -vanp tcp | grep 2222
tcp6       0      0  *.2222                 *.*                    LISTEN       131072  131072  43379      0 00100 00000006 00000000003e3959 00000001 00000800      1      0 000001
tcp6       0      0  ::1.58090              ::1.2222               TIME_WAIT    403715  146808  43387      0 02131 00000008 00000000003e3f04 00080081 04080800      0      0 000001
```

These are the titles:
```
Active Internet connections (including servers)
Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)      rhiwat  shiwat    pid   epid state  options           gencnt    flags   flags1 usscnt rtncnt fltrs
```

So, for example, killing PIDs 43379 and 43387

To extract the PID something like:
```
$ netstat -vanp tcp | grep 2222 | awk '/\.2222/ {print $9}'
```