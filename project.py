from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash,
                   Blueprint)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import json
from login import login

app = Flask(__name__)

app.register_blueprint(login)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Show all items
@app.route('/')
@app.route('/items/')
def showItems():
    items = session.query(Item).all()
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template(
        'latestItems.html',
        items=items,
        categories=categories)

#json data of all items
@app.route('/items/JSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(items=[r.serialize for r in items])

#show items by category
@app.route('/<int:category_id>/items/')
def showByCategory(category_id):
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('categoryItems.html', items=items)

#show item details
@app.route('/item/<int:item_id>/')
def showItemDetails(item_id):
    item, cat_id = session.query(
        Item, Item.category_id).filter_by(
        id=item_id).one()
    category = session.query(Category.name).filter_by(id=cat_id).one()[0]
    return render_template('itemDetails.html', item=item, category=category)

#create a new item
@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    elif request.method == 'POST':
        category_id = session.query(
            Category.id).filter_by(
            name=request.form['category']).one()[0]
        newItem = Item(
            name=request.form['name'],
            price=request.form['price'],
            description=request.form['description'],
            category_id=category_id,
            user_id=login_session['user_id']
        )
        session.add(newItem)
        flash('New Item %s Successfully Created' % newItem.name)
        session.commit()
        return redirect(url_for('showItems'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('newItem.html', categories=categories)

#edit item
@app.route('/edit/<int:item_id>/', methods=['GET', 'POST'])
def editItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    elif request.method == 'POST':
        editItem = session.query(Item).filter_by(id=item_id).one()
        if request.form['name']:
            editItem.name = request.form['name']
        if request.form['price']:
            editItem.price = request.form['price']
        if request.form['description']:
            editItem.description = request.form['description']
        if request.form['category']:
            category_id = session.query(
                Category.id).filter_by(
                name=request.form['category']).one()[0]
            editItem.category_id = category_id
        session.add(editItem)
        flash('Item %s Successfully Edited' % editItem.name)
        session.commit()
        return redirect(url_for('showItems'))
    else:
        categories = session.query(Category).order_by(asc(Category.name))
        item, cat, user = session.query(
            Item, Item.category_id, Item.user_id).filter_by(
            id=item_id).one()
        selectedCategory = session.query(
            Category.name).filter_by(
            id=cat).one()[0]
        email_id = session.query(User.email).filter_by(id=user).one()[0]
        if login_session['email'] == email_id:
            return render_template(
                'editItem.html',
                categories=categories,
                item=item,
                selectedCategory=selectedCategory)
        else:
            flash(
                'Item %s can not be  Edited since you are not the owner' %
                item.name)
            return redirect(url_for('showItemDetails', item_id=item_id))

#delete item
@app.route('/delete/<int:item_id>/', methods=['GET', 'POST'])
def deleteItem(item_id):
    if 'username' not in login_session:
        return redirect('/login')
    elif request.method == 'POST':
        itemToDelete = session.query(Item).filter_by(id=item_id).one()
        session.delete(itemToDelete)
        session.commit()
        flash('Item %s Successfully Deleted' % itemToDelete.name)
        return redirect(url_for('showItems'))
    else:
        item, user = session.query(Item, Item.user_id).filter_by(
            id=item_id).one()
        email_id = session.query(User.email).filter_by(id=user).one()[0]
        if login_session['email'] == email_id:
            return render_template('deleteItem.html', item=item)
        else:
            flash(
                'Item %s can not be  deleted since you are not the owner' %
                item.name)
            return redirect(url_for('showItemDetails', item_id=item_id))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
