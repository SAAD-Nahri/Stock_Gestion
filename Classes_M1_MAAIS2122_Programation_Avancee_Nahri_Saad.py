# auteur = Nahri Saad
# Master MAAIS 2021-2022
# programation avancée
# Poo Project de gestion de stock


import json
from utility_M1_MAAIS2122_Programation_Avancee_Nahri_Saad import *

# we will write a class that will handle all the class that will inherited from(create,delete,update,retrieve)
# and also will handle input validation we will use json file to store our data we use the Sqlite approach such
# as table for each class(client,order,product...) and relation between table(foreignkey relation..)

# in our stock management app the main approach is we will handle all the future and we will let the client
# do the order them self(that will avoid the of extra work)
# and we will handle the rest as we will see in the project code

# ======================================================================================================================
class Class_Manager:
    # the json file name that will store all the information
    file_name = "coo"
    TVA = 0.2

    def __init__(self):
        # every object will have an id equal the id of the previous(the same kind) incremented by one
        if self.all_item(False):
            self.id = int(list(self.all_item(False).keys())[-1])+1
        else:
            self.id = 0

    # check if a object dictionary existe in our json file
    @classmethod
    def existe_in_file(cls):
        try:
            b = cls.all_item()[str(cls.__name__)]
            return True
        except:
            return False
    # save an object in our json file
    def save(self):
        a = self.all_item()
        if not(self.existe_in_file()):
            a[str(self.__class__.__name__)] = {}
        a[str(self.__class__.__name__)][str(getattr(self, 'id'))] = self.__dict__
        with open(f"{self.file_name}.json", "w") as file:
            json.dump(a, file)

        # setattr(globals()[self.__class__.__name__], "id", getattr(globals()[self.__class__.__name__], 'id')+1)

    # get list of objects by there id
    @classmethod
    def get_elem_by_id(cls,*args):
        for i in args:
            if str(i) in cls.all_item(False).keys():
                yield cls.all_item(False)[str(i)]

    # search objects with the desire filter and "__" for range filter and "___" for attribute in the parent relation obj
    @classmethod
    def get_elem_filter(cls, include=True, **kwargs):
        # if no kwargs pass it return all the objects
        if kwargs:
            for elem in cls.all_item(False).values():
                obj = cls.dict_to_obj(elem)
                a = []
                for key, val in kwargs.items():
                    if "___" in key:
                        var1, var2 = key.split("___")
                        if "__" in var2:
                            var = getattr(getattr(obj, var1), var2.replace("__",""))
                            if var2.replace("__","") in getattr(getattr(obj, var1), "attr").keys() and "date" in getattr(getattr(obj, var1), "attr")[var2.replace("__","")]:
                                var = str_to_date(var)
                            e = var > val[0]
                            b = var < val[1]
                            c = e and b
                            a.append(c)
                        else:
                            c = str(getattr(getattr(obj, key.split("___")[0]), key.split("___")[1])) == str(val)
                        a.append(c)
                    elif "__" in key:
                        var = getattr(obj, key.split("__")[0])
                        if key.split("__")[0] in getattr(obj,"attr").keys() and "date" in getattr(obj,"attr")[key.split("__")[0]]:
                            var = str_to_date(var)
                        e = var > val[0]
                        b = var < val[1]
                        c = e and b
                        a.append(c)
                    else:
                        a.append(str(getattr(obj, key)) == str(val))
                if include:
                    # if no false in a it mean that all the filter are meet
                    if not(False in a):
                        yield elem
                else:
                    # here it exclude rather than include
                    if a != list(kwargs.values()):
                        yield elem
        else:
            for elem in cls.all_item(False).values():
                yield elem

    # just an extend to the previous function as it return dict, and this return obj
    # we can do it in get_elem_filter function by using additional kwargs argument obj=True

    @classmethod
    def get_all_obj_filter(cls, include=True, **kwargs):
        for obj in cls.get_elem_filter(include,**kwargs):
            # dict_to_obj take dict and return instance of object
            yield cls.dict_to_obj(obj)

    # search object by one or many filter they choose
    @classmethod
    def cherche_elem1(cls,**kwargs):
        li = getattr(cls, "attr").copy()
        for key, val in getattr(cls, "attr").items():
            if "non_field" in val:
                del li[key]
        l = list(li.keys())
        if len(l) > 1:
            print('taper le nombre de champ que tu veut filter par')
        filt = input_multiple_in_list(l)
        return cls.get_all_obj_filter(**filt,**kwargs)

    # take dict as argument and return instance of the class object
    @classmethod
    def dict_to_obj(cls, d):
        obj = cls()
        for key,val in d.items():
            setattr(obj, key, val)
        return obj

    # open json file and fetch all the data from it
    @classmethod
    def all_item(cls, all=True):
        with open(f"{cls.file_name}.json", "r") as file:
            a = json.load(file)
        if all:
            return a
        else:
            # if all equal to false it return only the data of the class table as a dict
            # that have id of the class instance as keys and data for instance as values
            if not (cls.existe_in_file()):
                return {}
            return a[str(cls.__name__)]

    # return list of object sorted by the parameter given in the definition of the class
    # it is possible to sort by the kwargs like we did in get_elem_filter(__,___)
    @classmethod
    def all_obj_sorted(cls, include=True, **kwargs):
        if "sort" in getattr(cls, "attr").keys():
            s = getattr(cls, "attr")['sort'].split()[-1]
            if "date" in getattr(cls, "attr")[s]:
                return list(cls.get_all_obj_filter(include, **kwargs)).sort(
                    key=lambda x: str_to_date(getattr(x, s)))
            return list(cls.get_all_obj_filter(include, **kwargs)).sort(
                key=lambda x: getattr(x, getattr(cls, "attr")['sort'].split()[-1]))

    # remove the instance from the json file
    def remove(self):
        a = self.all_item()
        # if the object have relation and get deleted we delete all the object related to it
        if "relation_child" in a[str(self.__class__.__name__)][str(self.id)].keys():
            for elem in a[str(self.__class__.__name__)][str(self.id)]["relation_child"].split()[-1].split("-"):
                for k in getattr(self, elem.split(":")[0]):
                    k.remove()
        del a[str(self.__class__.__name__)][str(self.id)]
        with open(f"{self.file_name}.json", "w") as file:
            json.dump(a,file)

    # this very important function as it handle the update of all object
    # and also carrie out the relation between class(when update on parent object it updated on all object related)
    #
    def update_elem(self):
        li = getattr(self,"attr").copy()
        for key,val in getattr(self,"attr").items():
            if "non_saisie" in val or "non_field" in val:
                del li[key]
        l = list(li.keys())
        if len(l)>=2:
            print('taper le nombre de champ que tu veut modifie')
        atr = input_in_list(l)
        val = getattr(self, atr)
        print(f"the old value of {atr} is:{val}")
        val1 = self.input_check(atr,getattr(self,"attr")[str(atr)],True)
        if val1 == -1:
            return -1
        # it remove the old instance fron the file
        if self.remove() == -1:
            return -1
        if "relation_child" in getattr(self,"attr").keys() and atr == "id":
            for elem in getattr(self,"attr")["relation_child"].split()[-1].split("-"):
                for k in getattr(self, elem.split(":")[0]):
                    setattr(k, elem.split(":")[1], val1)
                    k.save()
        setattr(self,atr,val1)
        # and save the new one
        self.save()

    # this function handle all the creation of object and check to validate the inpute
    # as(unique field, relation field,date field)
    # also we can pass data that we not want the user to input
    def create_elem(self, **kwargs):
        s = getattr(self,"attr")
        for key,val in s.items():
            if key in kwargs.keys():
                setattr(self, key, kwargs[str(key)])
            else:
                if "non_field" in val or "non_saisie" in val:
                    continue
                ipt = self.input_check(key,val)
                if ipt == -1:
                    return -1
                setattr(self,key,ipt)

    # ensure that the input is satisfied the requirement
    def input_check(self, a, b, update=False):
        if "relation" in b:
            c = (b.split()[-1]).split(':')[-1]
            obj_cls_name, relation_key = c.split('<->')
            z = list(getattr(globals()[str(obj_cls_name)], "get_elem_filter")())
            if z:
                if len(z) != 1:
                    print(f'select the value of {a} from the list of {obj_cls_name}')
                return input_in_list(z)[str(relation_key)]
            else:
                # in case the parent object not exist it send the user to created it
                print(f"we does not have any {obj_cls_name} in database, you must create one first")
                print("do you want to add it now:")
                a = input_in_list(["yes","no"])
                if a == "yes":
                    e = globals()[str(obj_cls_name)]()
                    if e.create_elem() != -1:
                        e.save()
                        return e.id
                else:
                    return -1
        # for the input of type choice
        elif "choice" in b :
            c = (b.split()[-1]).split(':')[-1]
            choices = c.split('-')
            print(f'select the value of {a} from the list of choice')
            return input_in_list(choices)
        else:
            while True:
                if "date" in b : print("date format --> DD/MM/YYYY")
                print(f"enter the {a}")
                c = input("-->")
                if str(self.input_validation(a, b, c, update)) == str(c):
                    return self.input_validation(a, b, c, update)
                else:
                    # it print the error that accurate during enter data
                    print(self.input_validation(a, b, c, update))
                    print("do you want to cancel the operation: ")
                    # maybe he don't want to continue the process
                    if input_in_list(["yes","no"]) == "yes":
                        return -1

    # check the basic input validation and return the value or error message
    def input_validation(self, a, b, c, update=False):
        if "NotNull" in str(b):
            if c == '':
                return "this field can't be empty"
        if "date" in b:
            if not (is_date(c)):
                return f"does not match the date format DD/MM/YYYY, {c} must be in the correct date format"
        if "number" in b:
            if not (int_input(c)):
                return "this field must be an number"
            c = int(c)
        if "unique" in str(b):
            if update:
                if list(self.get_elem_filter(**{str(a): c})) and c != getattr(self, a):
                    return f"this field must be an unique, {c} already existe"
            else:
                if list(self.get_elem_filter(**{str(a): c})):
                    return f"this field must be an unique, {c} already existe"
        return c


# =====================================================================================================================

class Person(Class_Manager):
    # at every class definition we need to set the attr in order to communicated with the upper class
    # we make class the carried all the function a user able to do based of type(client or supplier)
    # the important is that we let the client handle the order them self and we been able to do so
    # by every time a new client saved we initiated a place in card.json he can add product to it
    # and confirmed the order to start a new one
    attr = {"id":"unique non_saisie number",
            "fullname":'unique NotNull',
            "date_added":"date non_saisie",
            "type":"choice:client-fourniseur",
            "pays":"NotNull",
            "code_postal":"number",
            "adresse":"",
            # relation_child used to make change when the the parent instance change
            # non_saisie is the attribute that the user not see
            "relation_child":"non_field order:person_id",
            # sort used to give the key to sort with
            "sort":"non_field date_added"}
    def __init__(self,fullname='',date_added=str(datetime.date.today()),type="",pays='',code_postal=0,adresse=''):
        # automatically generate the id (autoincrement) of every class
        super(Person, self).__init__()
        self.fullname = fullname
        self.date_added = date_added
        self.type = type
        self.pays = pays
        self.code_postal = code_postal
        self.adresse = adresse

    def __str__(self):
        return f"{self.type}:name={self.fullname},id={self.id},montant rast a payee = {self.montant_rest_a_payee}"

    # add a row in cart.json file for the new client or clear it to make new order
    def init_cart(self):
        try:
            with open("cart.json", 'r') as cart:
                a = json.load(cart)
        except:
            a = {}
        a[str(self.id)] = {}
        with open("cart.json", "w") as file:
            json.dump(a,file)

    # override the save methode to include creating a row in card for the new client
    def save(self):
        if self.type == "client":
            self.init_cart()
        super().save()

    # add a product to the card by the client or update it
    def add_to_cart(self,product_id,update=False):
        cart = Cart(self.id)
        if update:
            print(f"the old quantity is {cart.cart[str(product_id)]['quantity']}")
        while True:
            x = int_input1("entre the quantity:")
            q = next(Product.get_all_obj_filter(id=product_id)).quantity
            # check if we have sufficient quantity
            if x > q:
                print(f"only {q} left in stock")
                print("do you want to order a less quantity:")
                s = input_in_list(["yes", "no"])
                if s == "no":
                    return -1
            else:
                break
        cart.add(product_id, x)
        print(f"change saved")

    # loop trough all the item in the client cart and add them to the database
    def confirme_order_client(self):
        order = Order()
        order.create_elem(person_id=self.id)
        order.save()
        cart = Cart(self.id)
        a = cart.get_total_cost()
        if cart.cart:
            print(f"the total amount is {a}$")
            print("do you want to confirme this order:")
            if input_in_list(['yes','no']) == "yes":
                for item in cart:
                    e = OrderItem()
                    e.create_elem(order_id=order.id,product_id=item["product"].id,quantity=item["quantity"])
                    prod = next(Product.get_all_obj_filter(id=item["product"].id))
                    prod.quantity -= item["quantity"]
                    e.save()
                self.init_cart()
            else:
                order.remove()
        else:
            print("you have no product in the cart")

    # for order of a supplier we take care of it with this methode
    @staticmethod
    def pass_order_fourniseur(id):
        order = Order()
        order.create_elem(person_id=id)
        order.save()
        while True:
            item = OrderItem()
            if item.create_elem(order_id=order.id) != -1:
                item.save()
            print("do you want to add another order line")
            if input_in_list(["yes","no"]) == "no":
                break

    # return all the orders of a user
    def order(self,**kwargs):
        return list(Order.get_all_obj_filter(person_id=self.id,**kwargs))

    @property
    def montant_rest_a_payee(self):
        return sum((y.total_montant-y.montant_deja_Paye) for y in self.order())

# =====================================================================================================================

class Category(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "nom":'unique NotNull',
            "relation_child":"non_field product:category_id",
            "sort":"non_field nom"}

    def __init__(self,nom=''):
        super(Category, self).__init__()
        self.nom = nom

    def __str__(self):
        return f"id={self.id}, nom={self.nom}"


    def product(self,**kwargs):
        return list(Product.get_all_obj_filter(category_id=self.id,**kwargs))

# =====================================================================================================================

class Product(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "nom":'unique NotNull',
            "category_id":"number relation:Category<->id",
            "prix":"number",
            "quantity":"number",
            "seuil_de_camande":"number",
            'relation_child':'non_field order_item:product_id',
            "sort":"non_field prix"}

    def __init__(self,nom='',category_id='',prix=0,quantity=0,seuil_de_camande=0):
        super(Product, self).__init__()
        self.nom = nom
        self.category_id = category_id
        self.prix = prix
        self.quantity = quantity
        self.seuil_de_camande = seuil_de_camande

    def __str__(self):
        return f"id={self.id}, nom={self.nom}, prix={self.prix}, quantity in the stock={self.quantity}"

    def order_item(self,**kwargs):
        return list(OrderItem.get_all_obj_filter(product_id=self.id,**kwargs))

# =====================================================================================================================

class Order(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "person_id": "number relation:Person<->id",
            "date_de_cammande": "date non_saisie",
            'relation_child':"non_field paiement:order_id-order_item:order_id",
            "sort":"non_field total_montant"}

    def __init__(self, person_id='', date_de_cammande=str(datetime.date.today())):
        super(Order, self).__init__()
        self.person_id = person_id
        self.date_de_cammande = date_de_cammande

    def __str__(self):
        return f"id={self.id},{self.person.type}:{self.person_id},Total montant:{self.total_montant},etat_livraison={self.etat_livraison}"

    @property
    def etat_livraison(self):
        l = [obj for obj in self.order_item() if obj.livraison == "livree"]
        if len(l) == len(list(self.order_item())):
            return "totalement_livree"
        elif len(l) == 0:
            return "non_livree"
        else:
            return "partialement_livree"

    @property
    def montant_deja_Paye(self):
        return sum(obj.montant for obj in self.paiement())

    @property
    def etat_paiement(self):
        if self.montant_deja_Paye == self.total_montant:
            return "totalement_payee"
        elif self.montant_deja_Paye == 0:
            return "non_payee"
        else:
            return "partialement_payee"

    @property
    def total_montant_hors_tax(self):
        return sum(obj.montant_hors_taxs for obj in self.order_item())

    @property
    def total_tva(self):
        return self.total_montant_hors_tax*self.TVA

    @property
    def total_montant(self):
        return self.total_montant_hors_tax + self.total_tva

    @property
    def person(self):
        return next(Person.get_all_obj_filter(id=self.person_id))

    def paiement(self,**kwargs):
        return Paiement.get_all_obj_filter(order_id=self.id,**kwargs)

    def order_item(self,**kwargs):
        return OrderItem.get_all_obj_filter(order_id=self.id,**kwargs)

# =====================================================================================================================

class OrderItem(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "order_id": "number relation:Order<->id",
            "product_id": "number relation:Product<->id",
            "livraison": "non_saisie choice:non_livree-livree",
            "quantity": "number",
            "sort":"non_field montant_total"}

    def __init__(self, order_id=0, product_id=0, livraison="Non_livree", quantity=0):
        super(OrderItem, self).__init__()
        self.order_id = order_id
        self.product_id = product_id
        self.livraison = livraison
        self.quantity = quantity

    def __str__(self):
        return f"id={self.id},product:{self.product.nom};quantity:{self.quantity}"

    # override the input_check methode to check for the quantity allowd to order by the client
    # but it useless as we check it in time the client added the product to the cart
    def input_check(self, a, b ,update=False):
        print(self.order.person.type)
        if str(a) == "quantity" and self.order.person.type == "client":
            x = int_input1("entre the quantity:")
            if x > self.product.quantity:
                print(f"only {self.product.quantity} left in stock")
                print("do you want to order a less quantity:")
                sel = input_in_list(["yes","no"])
                if sel == "yes":
                    return self.input_check(a, b, update)
                else:
                    return -1
            else:
                return x
        else:
            return super().input_check(a, b, update)

    # when we remove update an order we must check if the product is already consumed by the client
    # to complete the delete or update process
    def check_modifie(self):
        prod = self.product
        if self.livraison == "livree" and prod.quantity > self.quantity:
            return True
        return False

    # override the remove methode to handle the product quantity in case the order is remove
    def remove(self):
        person = self.order.person
        prod = self.product
        if person.type == "client":
            prod.quantity += self.quantity
            prod.save()
        if person.type == "fourniseur":
            if self.check_modifie():
                prod.quantity -= self.quantity
                prod.save()
            else:
                return -1
        super().remove()

    # override the save methode to handle the product quantity in in stock
    def save(self):
        person = self.order.person
        prod = self.product
        if person.type == "client":
            prod.quantity -= self.quantity
            prod.save()
        if person.type == "fourniseur":
            if self.livraison == "livree":
                prod.quantity += self.quantity
                prod.save()
        super().save()

    @property
    def order(self):
        return next(Order.get_all_obj_filter(id=self.order_id))

    @property
    def product(self):
        return next(Product.get_all_obj_filter(id=self.product_id))

    @property
    def montant_hors_taxs(self):
        return self.product.prix*self.quantity

    @property
    def montant_tva(self):
        return self.montant_hors_taxs*self.TVA

    @property
    def montant_total(self):
        return self.montant_hors_taxs+self.montant_tva

# ======================================================================================================================

class Paiement(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "order_id": "number relation:Order<->id",
            "montant":"number",
            "date_payee":"date non_saisie",
            "mode_de_paiement":"choice:wire_transfere-cash"}

    def __init__(self,order_id='', montant=0,date_payee = str(datetime.date.today()), mode_de_paiement=''):
        super(Paiement, self).__init__()
        self.order_id = order_id
        self.montant = montant
        self.date_payee = date_payee
        self.mode_de_paiement = mode_de_paiement

    def __str__(self):
        return f"id={self.id},order id={self.order_id};montant={self.montant}"

    @property
    def order(self):
        return next(Order.get_all_obj_filter(id=self.order_id))

# =====================================================================================================================

# Cart class for trait cart.json
# we store in cart.json a dict that have keys client id and values a dict of the product id and quantity he order
class Cart:
    def __init__(self,person_id):
        self.person_id = person_id
        with open("cart.json",'r') as cart:
            self.cart = json.load(cart)[str(person_id)]

    def __len__(self):
        return len(self.cart)

    # it iterate trough the dict to add the product object to the value of the dict
    def __iter__(self):
        a = self.cart.copy()
        for p in a.keys():
            self.cart[str(p)]['product'] = next(Product.get_all_obj_filter(id=p))
            # if the client add it to the cart and not confirme the order
            # and other client order it it remove from the cart automatically
            if self.cart[str(p)]['quantity'] > self.cart[str(p)]['product'].quantity:
                print(f"{self.cart[str(p)]['product'].nom} is remove from cart only {self.cart[str(p)]['product'].quantity} left in stock")
                del self.cart[str(p)]
                e = Cart(self.person_id)
                e.remove(str(p))
        for item in self.cart.values():
            yield item

    # add product to cart.json
    def add(self, product_id, quantity=1):
        self.cart[str(product_id)] = {'quantity': quantity}
        self.save()

    # remove product from cart.json
    def remove(self, product_id):
        if product_id in self.cart.keys():
            del self.cart[product_id]
            self.save()

    # save in cart.json
    def save(self):
        with open("cart.json",'r') as cart:
            a = json.load(cart)
        a[str(self.person_id)] = self.cart
        with open("cart.json","w") as file:
            json.dump(a,file)

    # the total cost in the cart
    def get_total_cost(self):
        return sum(item['quantity'] * item['product'].prix for item in self)


if __name__ == '__main__':
    pass