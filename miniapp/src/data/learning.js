// Mimics GET /learning?collection_id={id}
const learning = {
    1: [
        {
            id: 'elephant',
            en: 'elephant',
            ru: 'слон',
            transcription: '/ˈel.ə.fənt/',
            contexts: [
                {
                    en: 'Where do elephants live?',
                    ru: 'Где живут слоны?',
                },
                {
                    en: 'We won a small stuffed elephant.',
                    ru: 'Мы даже выиграли маленького плюшевого слонёнка.',
                },
                {
                    en: 'Habitat destruction forced a decline in elephant populations.',
                    ru: 'Даже в древности разрушение среды обитания вызывало сокращение популяций слонов.',
                },
            ],
        },
        {
            id: 'giraffe',
            en: 'giraffe',
            ru: 'жираф',
            transcription: '/dʒɪˈræf/',
            contexts: [
                { en: 'The giraffe has a very long neck.', ru: 'У жирафа очень длинная шея.' },
                { en: 'We saw a giraffe at the zoo.', ru: 'Мы видели жирафа в зоопарке.' },
                { en: 'Giraffes eat leaves from tall trees.', ru: 'Жирафы едят листья с высоких деревьев.' },
            ],
        },
        {
            id: 'zebra',
            en: 'zebra',
            ru: 'зебра',
            transcription: '/ˈziː.brə/',
            contexts: [
                { en: 'Zebras have black and white stripes.', ru: 'У зебр черно-белые полоски.' },
                { en: 'The zebra ran across the plain.', ru: 'Зебра побежала через равнину.' },
                { en: 'A zebra can run very fast.', ru: 'Зебра может бегать очень быстро.' },
            ],
        },
        {
            id: 'lion',
            en: 'lion',
            ru: 'лев',
            transcription: '/ˈlaɪ.ən/',
            contexts: [
                { en: 'The lion is known as the king of the jungle.', ru: 'Льва называют королём джунглей.' },
                { en: 'We heard the lion roar.', ru: 'Мы услышали рев льва.' },
                { en: 'Lions live in groups called prides.', ru: 'Львы живут в группах, которые называются прайдами.' },
            ],
        },
        {
            id: 'penguin',
            en: 'penguin',
            ru: 'пингвин',
            transcription: '/ˈpɛŋ.ɡwɪn/',
            contexts: [
                { en: 'Penguins live in cold places.', ru: 'Пингвины живут в холодных местах.' },
                { en: 'A baby penguin is very fluffy.', ru: 'Малыш-пингвин очень пушистый.' },
                { en: 'Penguins swim better than they walk.', ru: 'Пингвины лучше плавают, чем ходят.' },
            ],
        },
    ],
    2: [
        {
            id: 'teacher',
            en: 'teacher',
            ru: 'учитель',
            transcription: '/ˈtiː.tʃər/',
            contexts: [
                { en: 'The teacher explained the lesson.', ru: 'Учитель объяснил урок.' },
                { en: 'She became a math teacher.', ru: 'Она стала учителем математики.' },
                { en: 'The teacher gave us homework.', ru: 'Учитель дал нам домашнее задание.' },
            ],
        },
        {
            id: 'doctor',
            en: 'doctor',
            ru: 'врач',
            transcription: '/ˈdɒk.tər/',
            contexts: [
                { en: 'The doctor checked my temperature.', ru: 'Доктор измерил мою температуру.' },
                { en: 'I visited the doctor last week.', ru: 'Я ходил к врачу на прошлой неделе.' },
                { en: 'Doctors help people feel better.', ru: 'Врачи помогают людям выздоравливать.' },
            ],
        },
        {
            id: 'engineer',
            en: 'engineer',
            ru: 'инженер',
            transcription: '/ˌen.dʒɪˈnɪər/',
            contexts: [
                { en: 'The engineer designed a new bridge.', ru: 'Инженер спроектировал новый мост.' },
                { en: 'My brother is a software engineer.', ru: 'Мой брат — инженер-программист.' },
                { en: 'Engineers solve technical problems.', ru: 'Инженеры решают технические проблемы.' },
            ],
        },
        {
            id: 'chef',
            en: 'chef',
            ru: 'шеф-повар',
            transcription: '/ʃef/',
            contexts: [
                { en: 'The chef prepared a delicious meal.', ru: 'Шеф-повар приготовил вкусную еду.' },
                { en: 'He trained for years to become a chef.', ru: 'Он учился много лет, чтобы стать шеф-поваром.' },
                { en: 'Chefs create new recipes.', ru: 'Шеф-повара создают новые рецепты.' },
            ],
        },
        {
            id: 'firefighter',
            en: 'firefighter',
            ru: 'пожарный',
            transcription: '/ˈfaɪəˌfaɪ.tər/',
            contexts: [
                { en: 'The firefighter rescued the cat.', ru: 'Пожарный спас кошку.' },
                { en: 'Firefighters wear heavy gear.', ru: 'Пожарные носят тяжёлую экипировку.' },
                { en: 'The firefighter bravely entered the burning house.', ru: 'Пожарный смело вошел в горящий дом.' },
            ],
        },
    ],
    3: [
        {
            id: 'broom',
            en: 'broom',
            ru: 'метла',
            transcription: '/bruːm/',
            contexts: [
                { en: 'I swept the floor with a broom.', ru: 'Я подмёл пол метлой.' },
                { en: 'She bought a new broom yesterday.', ru: 'Она купила новую метлу вчера.' },
                { en: 'A broom is useful for cleaning.', ru: 'Метла полезна для уборки.' },
            ],
        },
        {
            id: 'vacuum',
            en: 'vacuum',
            ru: 'пылесос',
            transcription: '/ˈvæk.juːm/',
            contexts: [
                { en: 'I use a vacuum to clean the carpet.', ru: 'Я использую пылесос для чистки ковра.' },
                { en: 'The vacuum cleaner is broken.', ru: 'Пылесос сломался.' },
                { en: 'We vacuum the house every Saturday.', ru: 'Мы пылесосим дом каждую субботу.' },
            ],
        },
        {
            id: 'mop',
            en: 'mop',
            ru: 'швабра',
            transcription: '/mɒp/',
            contexts: [
                { en: 'He cleaned the kitchen floor with a mop.', ru: 'Он убрал пол на кухне шваброй.' },
                { en: 'The mop needs to dry.', ru: 'Швабра должна высохнуть.' },
                { en: 'Please use the mop for spills.', ru: 'Пожалуйста, используйте швабру для уборки пролитого.' },
            ],
        },
        {
            id: 'bucket',
            en: 'bucket',
            ru: 'ведро',
            transcription: '/ˈbʌk.ɪt/',
            contexts: [
                { en: 'Fill the bucket with water.', ru: 'Наполните ведро водой.' },
                { en: 'I carried a bucket of soap.', ru: 'Я нёс ведро с мыльной водой.' },
                { en: 'The bucket was too heavy.', ru: 'Ведро было слишком тяжёлым.' },
            ],
        },
        {
            id: 'duster',
            en: 'duster',
            ru: 'пыльник',
            transcription: '/ˈdʌs.tər/',
            contexts: [
                { en: 'She wiped the shelves with a duster.', ru: 'Она вытерла полки пыльником.' },
                { en: 'The duster is kept in the closet.', ru: 'Пыльник хранится в шкафу.' },
                { en: 'Use a duster for delicate surfaces.', ru: 'Используйте пыльник для деликатных поверхностей.' },
            ],
        },
    ],
}

export default learning;
