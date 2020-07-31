// Busca por tenista:

const  SITE = 'http://localhost:5000/'

let apiPause = false
let playerQuery = ''
let status

const playerSearch = document.querySelector('#player-searchbar')

if (playerSearch) {
  status = playerSearch.querySelector('.status')
  playerSearch.querySelector('input').addEventListener('input', function(){playerQuery = this.value})
  playerSearch.querySelector('input').addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
      if (playerQuery.length >= 3) {
        getPlayerNames(playerQuery)
      }
    }
  })
  playerSearch.querySelector('#searchPlayers').addEventListener('click', () => {
    if (playerQuery.length >= 3) {
      getPlayerNames(playerQuery)
    }
  })
}

function getPlayerNames(query) {
  if (!apiPause) {
    playerSearch.querySelector('.search-content').innerHTML = ''
    status.innerHTML = `<i class="fa fa-hourglass" id="searchPlayers"></i>`
    status.style.cursor = 'auto'
    fetch(SITE + `api/players?query=${query}`)
    .then(response => response.json())
    .then(players => {
      if (players.length === 0) {
        searchBoxShowError('Nenhum resultado encontrado')
      } else {
        populatePlayerSearchbox(players)
      }
      status.innerHTML = `<i class="fa fa-pause" id="searchPlayers"></i>`
      status.style.cursor = 'auto'
      apiPause = true
      setTimeout(() => {
        apiPause = false
        status.innerHTML = `<i class="fa fa-search" id="searchPlayers"></i>`
        status.style.cursor = 'pointer'
        status.addEventListener('click', () => {
          if (playerQuery.length >= 3) {
            getPlayerNames(playerQuery)
          }
        })
      }, 6000)
    })
    .catch((error) => {
      console.log(error)
      apiPause = false
      searchBoxShowError('Erro ao realizar busca')
      status.innerHTML = `<i class="fa fa-search" id="searchPlayers"></i>`
      status.style.cursor = 'pointer'
      status.addEventListener('click', () => {
        if (playerQuery.length >= 3) {
          getPlayerNames(playerQuery)
        }
      })
    })
  }
}

function populatePlayerSearchbox(playerData) {
  const searchContent = playerSearch.querySelector('.search-content')
  let close = document.createElement('div')
  close.classList.add('clear')
  close.innerHTML = '<i class="fa fa-times-circle"></i>'
  close.addEventListener('click', () => searchContent.innerHTML = '')
  searchContent.appendChild(close)
  playerData.forEach((player) => {
    let link = document.createElement('a')
    link.href = SITE + 'tenistas/' + player.id
    link.innerText = player.first_name + ' ' + player.last_name
    searchContent.appendChild(link)
  })
  searchContent.style.display = 'block'
}

function searchBoxShowError(message) {
  const searchContent = playerSearch.querySelector('.search-content')
  searchContent.innerHTML = `<div class="error"><i class="fa fa-exclamation-circle"></i> ${message}</div>`
  searchContent.style.display = 'block'
}


// Barra de navegação do admin:

const navParents = [...document.querySelectorAll('.nav-nested')]
if (navParents.length > 0) {
  navParents.forEach((node) => {
    node.addEventListener('click', () => {
      navParents.forEach((nav) => {
        nav.classList.remove('active')
        nav.querySelector('.nav-subitems-container').classList.add('hidden')
      })
      node.querySelector('.nav-subitems-container').classList.remove('hidden')
      node.classList.add('active')
    })
  })
  document.querySelector('main').addEventListener('click', () => {
    navParents.forEach((nav) => {
      nav.classList.remove('active')
      nav.querySelector('.nav-subitems-container').classList.add('hidden')
    })
  })
}

// Form novo player

const playerForm = document.querySelector('form.new-player-container')
if (playerForm) {
  const playerFormPic = playerForm.querySelector('img')
  const picUrlField = playerForm.querySelector('.field.url')
  picUrlField.querySelector('input').addEventListener('input', function() {
    playerFormPic.src = this.value
  })
  const eraser = playerForm.querySelector('.eraser')
  if (eraser) {
    eraser.addEventListener('click', () => {
      let inputs = [...playerForm.querySelectorAll('input')]
      inputs.forEach((input) => {
        input.value = null
      })
      let hand = playerForm.querySelector('select')
      hand.value = 'U'
    })
  }
}

// Form novo torneio

const newTForm = document.querySelector('.new-t-container')
if (newTForm) {
  const eraser = newTForm.querySelector('.eraser')
  if (eraser) {
    eraser.addEventListener('click', () => {
      let inputs = [...newTForm.querySelectorAll('input')]
      inputs.forEach((input) => {
        input.value = null
      })
      newTForm.querySelector('#cat').value = 'A'
      newTForm.querySelector('#surface').value = 'U'
    })
  }
}

// Form nova partida 

const newMatchForm = document.querySelector('.new-match-container')
if (newMatchForm) {
  const eraser = newMatchForm.querySelector('.eraser')
  if (eraser) {
    eraser.addEventListener('click', () => {
      let inputs = [...newMatchForm.querySelectorAll('input')]
      inputs.forEach((input) => {
        input.value = null
      })
      newMatchForm.querySelector('#t-round').value = 'RR'
      newMatchForm.querySelector('#bestof').value = 3
    })
  }
  const idField = newMatchForm.querySelector('#t-id')
  const nameField = newMatchForm.querySelector('#t-name')
  idField.addEventListener('input', () => {
    let tid = idField.value
    if (tid.length > 0) {
      let tname = newMatchForm.querySelector(`#tid-${tid}`)
      if (tname) {
        nameField.innerText = tname.innerText
      } else {
        nameField.innerText = '?'
      }
    }
  })
}

if (document.querySelector('.player-searchbar.search-winner')) {
  let container = document.querySelector('.player-searchbar.search-winner')
  const winBox = {
    container,
    'displayName': document.querySelector('#w-name'),
    'displayId': document.querySelector('#winner-id'),
    'status': container.querySelector('.status'),
    'searchContent': container.querySelector('.search-content'),
    'queryInput': container.querySelector('input'),
    'clear': () => {
      container.querySelector('.search-content').innerHTML = ''
    },
    'showError': (message) => {
      container.querySelector('.search-content').innerHTML = `<div class="error"><i class="fa fa-exclamation-circle"></i> ${message}</div>`
    },
    'wait': () => {
      let status = container.querySelector('.status')
      status.innerHTML = `<i class="fa fa-hourglass"></i>`
      status.style.cursor = 'auto'
    },
    'reset': () => {
      let status = container.querySelector('.status')
      status.innerHTML = `<i class="fa fa-search"></i>`
      status.style.cursor = 'pointer'
    }
  }
  winBox.status.addEventListener('click', () => {
    if (winBox.queryInput.value.length >= 3) {
      searchPlayerNames(winBox)
    }
  })
}

if (document.querySelector('.player-searchbar.search-winner')) {
  let container = document.querySelector('.player-searchbar.search-loser')
  const loseBox = {
    container,
    'displayName': document.querySelector('#l-name'),
    'displayId': document.querySelector('#loser-id'),
    'status': container.querySelector('.status'),
    'searchContent': container.querySelector('.search-content'),
    'queryInput': container.querySelector('input'),
    'clear': () => {
      container.querySelector('.search-content').innerHTML = ''
    },
    'showError': (message) => {
      container.querySelector('.search-content').innerHTML = `<div class="error"><i class="fa fa-exclamation-circle"></i> ${message}</div>`
    },
    'wait': () => {
      let status = container.querySelector('.status')
      status.innerHTML = `<i class="fa fa-hourglass"></i>`
      status.style.cursor = 'auto'
    },
    'reset': () => {
      let status = container.querySelector('.status')
      status.innerHTML = `<i class="fa fa-search"></i>`
      status.style.cursor = 'pointer'
    }
  }
  loseBox.status.addEventListener('click', () => {
    if (loseBox.queryInput.value.length >= 3) {
      searchPlayerNames(loseBox)
    }
  })
}

function searchPlayerNames(box) {
  const status = box.status
  const query = box.queryInput.value
  box.clear()
  box.wait()
  fetch(SITE + `api/players?query=${query}`)
  .then(response => response.json())
  .then(players => {
    if (players.length === 0) {
      box.showError('Nenhum resultado encontrado')
    } else {
      populateMatchFormSearchbox(players, box)
    }
    box.reset()
    status.addEventListener('click', () => {
      if (box.queryInput.value.length >= 3) {
        searchPlayerNames(box)
      }
    })
  })
  .catch((error) => {
    console.log(error)
    box.showError('Erro ao realizar busca')
    box.reset()
    status.addEventListener('click', () => {
      if (query.length >= 3) {
        searchPlayerNames(box)
      }
    })
  })
}

function populateMatchFormSearchbox(playerData, box) {
  let close = document.createElement('div')
  close.classList.add('clear')
  close.innerHTML = '<i class="fa fa-times-circle"></i>'
  close.addEventListener('click', () => box.searchContent.innerHTML = '')
  box.searchContent.appendChild(close)
  playerData.forEach((player) => {
    let line = document.createElement('div')
    line.classList.add('button')
    line.innerText = player.first_name + ' ' + player.last_name
    line.addEventListener('click', () => {
      box.displayName.innerText = player.first_name + ' ' + player.last_name
      box.displayId.value = player.id
      box.searchContent.innerHTML = ''
    })
    box.searchContent.appendChild(line)
  })
  box.searchContent.style.display = 'block'
}

// Chaves torneios

const tInfo = document.querySelector('.t-info')
const mList = document.querySelector('.match-list')

if (tInfo && mList) {
  const main = document.querySelector('main')
  let mData = {
    'F': [],
    'SF': [],
    'QF': [],
    'R16': [],
    'R32': []
  }
  const rows = [...mList.querySelector('tbody').querySelectorAll('tr')]
  rows.forEach((row) => {
    let cells = [...row.querySelectorAll('td')]
    let link = cells[3].querySelector('a').href
    let rowData = cells.map((cell) => {
      return cell.innerText
    })
    let bracketId = Object.keys(mData).indexOf(rowData[3])
    let wName = rowData[5]
    if (wName) {
      wName = wName.split(' ')
      wName = wName.pop()
    } else {
      wName = ''
    }
    let lName = rowData[6]
    if (lName) {
      lName = lName.split(' ')
      lName = lName.pop()
    } else {
      lName = ''
    }
    if (bracketId >= 0) {
      mData[rowData[3]].push({
        'number': rowData[4],
        wName,
        lName,
        link
      })
    }
  })
  const TournamentBrackets = createBrackets(mData)
  main.appendChild(TournamentBrackets)
  const bracketToggle = document.createElement('button')
  bracketToggle.innerHTML = '<i class="fa fa-th"></i> Ver Chaves'
  bracketToggle.type = 'button'
  bracketToggle.addEventListener('click', () => {
    TournamentBrackets.style.display = 'grid'
    window.scrollTo({
      top: 150,
      left: 0,
      behavior: 'smooth'
    })
  })
  document.querySelector('.show-brackets').appendChild(bracketToggle)
}

function createBrackets(mData) {
  const container = document.createElement('div')
  container.classList.add('tournament-brackets')
  container.style.display = 'none'
  container.style.gridColumnGap = '16px'
  container.style.gridTemplateColumns = 'repeat(8, 1fr)'
  container.style.gridAutoRows = '19px'
  for (let i = 0; i < 8; i ++) {
    let ro16L = makeBracket(mData['R32'][i])
    ro16L.style.gridColumn = '1 / 2'
    let start = 1 + i * 4
    ro16L.style.gridRow = `${start} / ${start+2}`
    ro16L.id = `ro16-${i}`
    ro16L.classList.add('ro16')
    container.appendChild(ro16L)
  }
  for (let i = 0; i < 8; i ++) {
    let ro16R = makeBracket(mData['R32'][i+8])
    ro16R.style.gridColumn = '8 / 9'
    let start = 1 + i * 4
    ro16R.style.gridRow = `${start} / ${start+2}`
    ro16R.id = `ro16-${i+8}`
    ro16R.classList.add('ro16')
    container.appendChild(ro16R)
  }
  for (let i = 0; i < 4; i ++) {
    let ro8L = makeBracket(mData['R16'][i])
    ro8L.style.gridColumn = '2 / 3'
    let start = 3 + i * 8
    ro8L.style.gridRow = `${start} / ${start+2}`
    ro8L.id = `ro8L-${i}`
    ro8L.classList.add('ro8L')
    container.appendChild(ro8L)
  }
  for (let i = 0; i < 4; i ++) {
    let ro8R = makeBracket(mData['R16'][i+4])
    ro8R.style.gridColumn = '7 / 8'
    let start = 3 + i * 8
    ro8R.style.gridRow = `${start} / ${start+2}`
    ro8R.id = `ro8R-${i+4}`
    ro8R.classList.add('ro8R')
    container.appendChild(ro8R)
  }
  for (let i = 0; i < 2; i ++) {
    let ro4L = makeBracket(mData['QF'][i])
    ro4L.style.gridColumn = '3 / 4'
    let start = 7 + i * 16
    ro4L.style.gridRow = `${start} / ${start+2}`
    ro4L.id = `ro4L-${i}`
    ro4L.classList.add('ro4L')
    container.appendChild(ro4L)
  }
  for (let i = 0; i < 2; i ++) {
    let ro4R = makeBracket(mData['QF'][i+2])
    ro4R.style.gridColumn = '6 / 7'
    let start = 7 + i * 16
    ro4R.style.gridRow = `${start} / ${start+2}`
    ro4R.id = `ro4R-${i+2}`
    ro4R.classList.add('ro4R')
    container.appendChild(ro4R)
  }
  let ro2L = makeBracket(mData['SF'][0])
  ro2L.style.gridColumn = '4 / 5'
  ro2L.style.gridRow = '15 / 17'
  ro2L.id = 'ro2L-0'
  ro2L.classList.add('ro2L')
  container.appendChild(ro2L)
  let ro2R = makeBracket(mData['SF'][1])
  ro2R.style.gridColumn = '5 / 6'
  ro2R.style.gridRow = '15 / 17'
  ro2R.id = 'ro2R-1'
  ro2R.classList.add('ro2R')
  container.appendChild(ro2R)
  let ro1 = makeBracket(mData['F'][0])
  ro1.style.gridColumn = '4 / 6'
  ro1.style.gridRow = '2 / 4'
  ro1.querySelector('.bracket').classList.add('final')
  container.appendChild(ro1)
  const dismiss = document.createElement('button')
  dismiss.innerHTML = '<i class="fa fa-times"></i>'
  dismiss.style.position = 'absolute'
  dismiss.style.left = '50%'
  dismiss.style.top = '85%'
  dismiss.style.padding = '8px'
  dismiss.style.borderRadius = '50%'
  dismiss.type = 'button'
  dismiss.addEventListener('click', () => {
    container.style.display = 'none'
  })
  container.appendChild(dismiss)
  return container
}

function makeBracket({wName='', lName='', link=''}={}) {
  let anchor = document.createElement('a')
  anchor.href = link
  anchor.style.textDecoration = 'none'
  let bracket = document.createElement('div')
  bracket.classList.add('bracket')
  let winner = document.createElement('div')
  winner.classList.add('winner')
  winner.style.height = '50%'
  let loser = document.createElement('div')
  loser.classList.add('loser')
  loser.style.height = '50%'
  winner.style.marginTop = '2px'
  winner.style.marginLeft = '4px'
  loser.style.marginLeft = '4px'
  winner.innerText = wName.toUpperCase()
  winner.style.color = 'gold'
  loser.innerText = lName.toUpperCase()
  bracket.appendChild(winner)
  bracket.appendChild(loser)
  anchor.appendChild(bracket)
  return anchor
}

