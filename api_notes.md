
## Endpoints
### Accounts
/character-window/get-account-name

### Characters
/character-window/get-characters

### Items
/character-window/get-items&character=:name
```
:name {character name}
```

### Stash

/character-window/get-stash-items&league=:league&tabs=:showTabsInfo&tabIndex=:index
```
:league {Standard, Hardcore, ...}
:showTabsInfo {0, 1} -- 1 to show tabs name, position, colors
:index {0..N}
```

### Passives
/character-window/get-passive-skills&character=:name
```
:name {character name}
```

## Headers
### X-Rate-Limit-{Method}
```
{limit}:{interval (sec)}:{timeout}
```

### X-Rate-Limit-{Method}-State
```
{current hits}:{interval (sec)}:{timeout}
```

### X-Rate-Limit-Policy
```
{active policy on endpoint}
```

### X-Rate-Limit-Rules
```
{list of Methods}
```

### Retry-After
```
{if limited, time left on limit}
```