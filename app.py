from ctypes import alignment
from h2o_wave import Q, ui, app, main
import pickle

# Open pickle data file containing Label encoders, Scaler and Model
open_file = open("Data/Model_Data.pkl", "rb")
object_list = pickle.load(open_file)

Manufacturer_LE, Model_LE, Category_LE, Fuel_type_LE, Gear_LE, Drive_LE, Wheel_LE, Color_LE = object_list[
    0]
scaler = object_list[1]
model = object_list[2]
open_file.close()

# Open pickle data file containing categories for dropdown
open_file = open("Data/Labels.pkl", "rb")
Labels = pickle.load(open_file)
open_file.close()


async def loadPage(q):
    q.page['form_1'] = ui.form_card(
        box='1 2 3 5',
        items=[
            ui.dropdown(name='manufacturer', label='Manufacturer', popup='always', required=True, choices=[
                # creating choices from pickle files which contains categories
                ui.choice(name=label, label=label) for label in Labels[0]
            ]),
            ui.dropdown(name='model', label='Model', popup='always', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[1]
            ]),
            ui.textbox(name='year', label='Year of Manu.', required=True),
            ui.textbox(name='mileage', label='Mileage', required=True),
            ui.dropdown(name='category', label='Category', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[2]
            ]),
            ui.dropdown(name='fuel_type', label='Fuel Type', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[3]
            ]),
        ]
    )
    q.page['form_2'] = ui.form_card(
        box='4 2 3 5',
        items=[
            ui.slider(name='capcity', label='Engine volume (Liters)',
                      min=0.6, max=6, value=1, step=0.1),
            ui.slider(name='cylinders', label='Cylinders',
                      min=3, max=16, value=3, step=1),
            ui.dropdown(name='gear_box', label='Gear box type', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[4]
            ]),
            ui.dropdown(name='drive_wheels', label='Drive wheels', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[5]
            ]),
            ui.dropdown(name='color', label='Color', popup='always', required=True, choices=[
                ui.choice(name=label, label=label) for label in Labels[7]
            ]),
            ui.choice_group(name='drive_side', label='Drive side', inline=True, value='Right-hand', choices=[
                ui.choice(name='Left', label='Left'),
                ui.choice(name='Right-hand', label='Right'),
            ])
        ]
    )
    q.page['form_3'] = ui.form_card(
        box='7 2 3 5',
        items=[
            ui.button(name='Submit', label='Calculate', width='300px'),
            ui.text(f'Please enter your vehicle details')
        ]
    )

    if q.args.Submit:
        del q.page['form_3']
        # Check for missing dat in the form
        if not [x for x in (q.args.manufacturer, q.args.model, q.args.year, q.args.mileage, q.args.category, q.args.fuel_type, q.args.gear_box, q.args.drive_wheels, q.args.color,) if x == ""]:
            Year = int(q.args.year)
            Engine = int(q.args.capcity)
            Mileage = int(q.args.mileage)
            Cylinders = int(q.args.cylinders)
            Manufacturer = Manufacturer_LE.transform([q.args.manufacturer])[0]
            Model = Model_LE.transform([q.args.model])[0]
            Category = Category_LE.transform([q.args.category])[0]
            Fuel = Fuel_type_LE.transform([q.args.fuel_type])[0]
            Gear = Gear_LE.transform([q.args.gear_box])[0]
            Drive = Drive_LE.transform([q.args.drive_wheels])[0]
            Wheel = Wheel_LE.transform([q.args.drive_side])[0]
            Color = Color_LE.transform([q.args.color])[0]

            X = [[Year, Engine, Mileage, Cylinders, Manufacturer,
                  Model, Category, Fuel, Gear, Drive, Wheel, Color]]
            X = scaler.transform(X)
            pred = model.predict(X)
            price = int(pred[0])
            q.page['form_3'] = ui.form_card(
                box='7 2 3 5',
                items=[
                    ui.button(name='Submit', label='Calculate', width='300px'),
                    ui.text(f'Estimated Price: {price} USD')
                ]
            )
        else:
            # Error handling if missing field is found in form
            q.page['form_3'] = ui.form_card(
                box='7 2 3 5',
                items=[
                    ui.button(name='Submit', label='Calculate', width='300px'),
                    ui.text(
                        '<span style="color:red">Fill All Required Details.</span>')
                ]
            )

        await q.page.save()

    await q.page.save()


@app('/')
async def serve(q: Q):
    q.page['meta'] = ui.meta_card(
        box='',
        themes=[
            ui.theme(
                name='my-awesome-theme',
                primary='#FF9F1C',
                text='#e8e1e1',
                card='#000000',
                page='#070b1a',
            )
        ],
        theme='my-awesome-theme'
    )
    q.page['head'] = ui.header_card(
        box='1 1 10 1',
        title='Best Price Search',
        subtitle='Get the best price for your used vehicle.',
        icon='ExploreData',
    )

    await loadPage(q)
    await q.page.save()
